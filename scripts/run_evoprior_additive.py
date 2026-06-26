"""Run v0.9 integrated additive EvoPrior benchmarks."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from evoprior_aivc.baselines import (
    ControlMeanBaseline,
    GenePriorCorrectionBaseline,
    HierarchicalAdditiveBaseline,
    MeanDeltaBaseline,
    RidgeCVBaseline,
    build_delta_dataset,
)
from evoprior_aivc.baselines.base import DeltaDataset
from evoprior_aivc.baselines.lineage_shrinkage import LineageShrinkageBaseline
from evoprior_aivc.data.download import prepare_dataset
from evoprior_aivc.data.gene_prior_sources import prepare_gene_prior
from evoprior_aivc.data.preprocess import preprocess_adata
from evoprior_aivc.data.pseudobulk import aggregate_pseudobulk
from evoprior_aivc.data.real_loader import load_real_dataset
from evoprior_aivc.data.splits import assign_heldout_cell_type_split, heldout_cell_type_eligibility
from evoprior_aivc.data.synthetic_gene_prior import (
    make_synthetic_gene_prior_adata,
    make_synthetic_gene_prior_tree,
)
from evoprior_aivc.evaluation.component_audit import write_component_audit_report
from evoprior_aivc.evaluation.de_metrics import de_recovery_metrics
from evoprior_aivc.evaluation.evaluator import evaluate_delta_predictions, subset_delta_dataset
from evoprior_aivc.evaluation.leakage_checks import (
    assert_no_heldout_cell_type_target_leakage,
    assert_required_split_labels,
)
from evoprior_aivc.evaluation.statistics import summarize_metric_table
from evoprior_aivc.models import EvoPriorAdditiveModel
from evoprior_aivc.priors.cell_lineage import CellTypeLineageMapper, LineageTree
from evoprior_aivc.priors.gene_prior_table import GenePriorTable


def main() -> None:
    args = _parse_args()
    config = _load_yaml(Path(args.config))
    if config["mode"] == "synthetic_integrated_evoprior":
        run_synthetic(config)
    elif config["mode"] == "real_kang_evoprior_additive":
        run_real_kang(config)
    else:
        raise ValueError(f"unsupported mode: {config.get('mode')}")


def run_synthetic(config: dict[str, Any]) -> Path:
    adata, prior = make_synthetic_gene_prior_adata(seed=config["seed"], **config["synthetic"])
    tree = make_synthetic_gene_prior_tree()
    expression, metadata = aggregate_pseudobulk(
        adata,
        groupby=tuple(config["pseudobulk"]["groupby"]),
        min_cells=int(config["pseudobulk"]["min_cells"]),
        aggregation=config["pseudobulk"]["aggregation"],
    )
    dataset = build_delta_dataset(
        expression,
        metadata,
        control_label=config["delta"]["control_label"],
        match_columns=tuple(config["delta"]["match_columns"]),
    )
    run_dir = _make_run_dir(config)
    run_dir.mkdir(parents=True, exist_ok=False)
    _write_yaml(run_dir / "resolved_config.yaml", config)
    metrics, de_rows, subset_rows, split_manifest, component_store = _evaluate_heldouts(
        config,
        dataset,
        tree,
        None,
        prior,
        config["splits"]["heldout_cell_types"],
    )
    _write_outputs(run_dir, config, dataset, prior, metrics, de_rows, subset_rows, split_manifest)
    _write_component_audit(run_dir, config, component_store)
    _write_report(run_dir, config, metrics, subset_rows, "Synthetic Integrated EvoPriorAdditive")
    print(run_dir)
    return run_dir


def run_real_kang(config: dict[str, Any]) -> Path:
    data_config = _load_yaml(Path(config["data_config"]))
    lineage_config = _load_yaml(Path(config["lineage_config"]))
    gene_prior_config = _load_yaml(Path(config["gene_prior_config"]))
    prepare_dataset(data_config)
    prior_result = prepare_gene_prior(gene_prior_config)
    prior = GenePriorTable.from_csv(prior_result.feature_table_path)
    adata, schema_report = load_real_dataset(data_config)
    adata = preprocess_adata(adata, config)
    expression, metadata = aggregate_pseudobulk(
        adata,
        groupby=tuple(config["pseudobulk"]["groupby"]),
        min_cells=int(config["pseudobulk"]["min_cells"]),
        aggregation=config["pseudobulk"]["aggregation"],
    )
    dataset = build_delta_dataset(
        expression,
        metadata,
        control_label=config["delta"]["control_label"],
        match_columns=tuple(config["delta"]["match_columns"]),
        fallback=config["delta"].get("control_fallback", "raise"),
    )
    tree, mapper = _load_lineage(lineage_config)
    suite = config["splits"]["heldout_cell_type_suite"]
    eligibility = heldout_cell_type_eligibility(
        metadata,
        control_label=config["delta"]["control_label"],
        min_test_groups=int(suite["min_test_groups"]),
        min_control_groups=int(suite["min_control_groups"]),
        min_train_groups=int(suite["min_train_groups"]),
    )
    heldouts = eligibility.loc[eligibility["eligible"], "cell_type"].astype(str).tolist()
    run_dir = _make_run_dir(config)
    run_dir.mkdir(parents=True, exist_ok=False)
    _write_yaml(run_dir / "resolved_config.yaml", config)
    _write_yaml(run_dir / "resolved_gene_prior_config.yaml", gene_prior_config)
    _write_json(run_dir / "gene_prior_preparation.json", prior_result.to_dict())
    _write_json(run_dir / "schema_report.json", schema_report.__dict__)
    eligibility.to_csv(run_dir / "heldout_cell_type_eligibility.csv", index=False)
    metrics, de_rows, subset_rows, split_manifest, component_store = _evaluate_heldouts(
        config,
        dataset,
        tree,
        mapper,
        prior,
        heldouts,
        control_usage=config["splits"]["control_usage"],
    )
    _write_outputs(run_dir, config, dataset, prior, metrics, de_rows, subset_rows, split_manifest)
    _write_component_audit(run_dir, config, component_store)
    _write_report(run_dir, config, metrics, subset_rows, "Kang EvoPriorAdditive")
    print(run_dir)
    return run_dir


def _evaluate_heldouts(
    config: dict[str, Any],
    dataset: DeltaDataset,
    tree: LineageTree,
    mapper: CellTypeLineageMapper | None,
    prior: GenePriorTable,
    heldout_cell_types: list[str],
    *,
    control_usage: str = "control_observed_ood",
):
    metric_rows: list[dict[str, Any]] = []
    de_rows: list[dict[str, Any]] = []
    subset_rows: list[dict[str, Any]] = []
    split_frames: list[pd.DataFrame] = []
    component_store: dict[str, dict[str, list[pd.DataFrame]]] = {}
    shuffled = prior.shuffled_control(seed=909)
    for heldout in heldout_cell_types:
        split = assign_heldout_cell_type_split(dataset.metadata, heldout_cell_type=heldout)
        assert_required_split_labels(split, required_labels=("train", "test"))
        assert_no_heldout_cell_type_target_leakage(
            dataset.metadata,
            split,
            heldout_cell_type=heldout,
            control_usage=control_usage,
        )
        split_frames.append(_split_manifest(dataset.metadata, split, heldout))
        train = subset_delta_dataset(dataset, split == "train")
        test = subset_delta_dataset(dataset, split == "test")
        for baseline in _baseline_instances(config, tree, mapper, prior, shuffled):
            baseline.fit(train)
            if isinstance(baseline, EvoPriorAdditiveModel):
                components = baseline.predict_components(test)
                predicted = components["final_delta"]
                _append_components(component_store, baseline.name, components)
            else:
                predicted = baseline.predict_delta(test)
            metrics = evaluate_delta_predictions(test, predicted)
            metric_rows.append(
                {
                    "experiment_id": config["experiment_id"],
                    "dataset_id": config["dataset_id"],
                    "split_mode": "heldout_cell_type_suite",
                    "split": "test",
                    "heldout": heldout,
                    "baseline": baseline.name,
                    "n_train_examples": len(train.group_ids),
                    "n_test_examples": len(test.group_ids),
                    **metrics,
                }
            )
            subset_rows.extend(
                _subset_metric_rows(config, test, predicted, prior, heldout, baseline.name)
            )
            de_rows.extend(_de_rows(config, test, predicted, heldout, baseline.name))
    split_manifest = pd.concat(split_frames, ignore_index=True) if split_frames else pd.DataFrame()
    return (
        pd.DataFrame(metric_rows),
        pd.DataFrame(de_rows),
        pd.DataFrame(subset_rows),
        split_manifest,
        component_store,
    )


def _baseline_instances(
    config: dict[str, Any],
    tree: LineageTree,
    mapper: CellTypeLineageMapper | None,
    prior: GenePriorTable,
    shuffled_prior: GenePriorTable,
):
    lineage_kwargs = config.get("lineage_baseline", {})
    gene_kwargs = config["gene_prior_correction"]
    evo_kwargs = config["evoprior_additive"]
    gene_label = config.get("gene_prior_label", "hgnc_gene_prior")
    lineage_base = LineageShrinkageBaseline(
        tree=tree,
        mapper=mapper,
        **_lineage_kwargs(lineage_kwargs),
    )
    baselines = [
        ControlMeanBaseline(),
        MeanDeltaBaseline(fallback="global"),
        HierarchicalAdditiveBaseline(alpha=5.0),
        RidgeCVBaseline(alphas=(0.1, 1.0, 10.0)),
        LineageShrinkageBaseline(tree=tree, mapper=mapper, **_lineage_kwargs(lineage_kwargs)),
        GenePriorCorrectionBaseline(
            base_baseline=lineage_base,
            gene_prior=prior,
            **gene_kwargs,
        ),
        EvoPriorAdditiveModel(
            tree=tree,
            mapper=mapper,
            gene_prior=None,
            use_gene_prior=False,
            use_lineage_prior=True,
            **evo_kwargs,
        ),
        EvoPriorAdditiveModel(
            tree=tree,
            mapper=mapper,
            gene_prior=prior,
            use_gene_prior=True,
            use_lineage_prior=True,
            **evo_kwargs,
        ),
        EvoPriorAdditiveModel(
            tree=tree,
            mapper=mapper,
            gene_prior=shuffled_prior,
            use_gene_prior=True,
            use_lineage_prior=True,
            **evo_kwargs,
        ),
        EvoPriorAdditiveModel(
            tree=tree,
            mapper=mapper,
            gene_prior=prior,
            use_gene_prior=False,
            use_lineage_prior=True,
            gene_prior_mode="disabled",
            **evo_kwargs,
        ),
    ]
    labels = [
        "control_mean",
        "mean_delta",
        "hierarchical_additive",
        "ridge_cv",
        "lineage_shrinkage",
        "gene_prior_correction_lineage_shrinkage",
        "evoprior_additive_no_gene_prior",
        f"evoprior_additive_{gene_label}",
        "evoprior_additive_shuffled_gene_prior",
        "evoprior_additive_gene_prior_disabled",
    ]
    for baseline, label in zip(baselines, labels, strict=True):
        baseline.name = label
        yield baseline


def _lineage_kwargs(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "tau": float(raw.get("tau", 1.5)),
        "shrinkage": float(raw.get("shrinkage", 0.85)),
        "fallback_mode": raw.get("fallback_mode", "global"),
    }


def _subset_metric_rows(config, dataset, predicted, prior, heldout: str, baseline: str):
    coverage = prior.coverage_for_genes(dataset.gene_names)
    aligned = prior.align_to_genes(dataset.gene_names)
    covered_genes = list(aligned.index[~aligned["_prior_missing"]])
    missing_genes = list(aligned.index[aligned["_prior_missing"]])
    rows = []
    for label, genes in (
        ("prior_covered", covered_genes),
        ("prior_missing", missing_genes),
        ("prior_modulated", _prior_modulated_genes(config, dataset.gene_names)),
    ):
        genes = [gene for gene in genes if gene in dataset.gene_names]
        if not genes:
            continue
        observed = dataset.observed_delta.loc[:, genes].to_numpy(dtype=float)
        pred = predicted.loc[dataset.observed_delta.index, genes].to_numpy(dtype=float)
        rows.append(
            {
                "heldout": heldout,
                "baseline": baseline,
                "subset": label,
                "n_genes": len(genes),
                "coverage_fraction": coverage.coverage_fraction,
                "mae_delta": float(abs(observed - pred).mean()),
                "mse_delta": float(((observed - pred) ** 2).mean()),
            }
        )
    return rows


def _de_rows(config, dataset, predicted, heldout: str, baseline: str):
    rows = []
    for group_id in dataset.group_ids:
        row = de_recovery_metrics(
            dataset.observed_delta.loc[group_id].to_numpy(dtype=float),
            predicted.loc[group_id].to_numpy(dtype=float),
            ks=tuple(config["evaluation"]["de_ks"]),
        )
        row.update({"heldout": heldout, "baseline": baseline, "group_id": group_id})
        rows.append(row)
    return rows


def _prior_modulated_genes(config: dict[str, Any], gene_names: list[str]) -> list[str]:
    prefixes = config.get("evaluation", {}).get("prior_modulated_gene_prefixes", [])
    return [gene for gene in gene_names if any(str(gene).startswith(prefix) for prefix in prefixes)]


def _write_outputs(
    run_dir,
    config,
    dataset,
    prior,
    metrics,
    de_rows,
    subset_rows,
    split_manifest,
) -> None:
    metric_summary = summarize_metric_table(
        metrics,
        group_columns=("split_mode", "split", "baseline"),
        metric_columns=tuple(config["evaluation"]["metric_columns"]),
    )
    metrics.to_csv(run_dir / "metrics.csv", index=False)
    metric_summary.to_csv(run_dir / "metric_summary.csv", index=False)
    de_rows.to_csv(run_dir / "de_metrics.csv", index=False)
    _de_summary(de_rows).to_csv(run_dir / "de_summary.csv", index=False)
    subset_rows.to_csv(run_dir / "subset_metrics.csv", index=False)
    _subset_summary(subset_rows).to_csv(run_dir / "subset_metric_summary.csv", index=False)
    split_manifest.to_csv(run_dir / "split_manifest.csv", index=False)
    _write_json(
        run_dir / "run_manifest.json",
        {
            "git_commit": _git_commit(),
            "experiment_id": config["experiment_id"],
            "dataset_id": config["dataset_id"],
            "n_genes": len(dataset.gene_names),
            "gene_prior_coverage": prior.coverage_for_genes(dataset.gene_names).__dict__,
            "claim_boundary": config["reporting"]["claim_boundary"],
        },
    )


def _write_component_audit(run_dir, config, component_store) -> None:
    primary = f"evoprior_additive_{config.get('gene_prior_label', 'hgnc_gene_prior')}"
    components = _concat_components(component_store.get(primary, {}))
    shuffled = _concat_components(component_store.get("evoprior_additive_shuffled_gene_prior", {}))
    if components:
        summary = write_component_audit_report(
            run_dir / "component_audit.md",
            title=config["reporting"].get("audit_title", "v0.9 Component Audit"),
            components=components,
            shuffled_components=shuffled or None,
            claim_boundary=config["reporting"]["claim_boundary"],
        )
        _write_json(run_dir / "component_audit_summary.json", summary)


def _write_report(run_dir, config, metrics, subset_rows, title: str) -> None:
    metric_summary = summarize_metric_table(
        metrics,
        group_columns=("split_mode", "split", "baseline"),
        metric_columns=tuple(config["evaluation"]["metric_columns"]),
    )
    lines = [
        f"# v0.9 {title} Report",
        "",
        "## Executive Summary",
        "",
        "Integrated additive model run completed. Interpret metrics only within this run's split.",
        "",
        "## Claim Boundary",
        "",
        config["reporting"]["claim_boundary"],
        "",
        "## Ablation Table",
        "",
        _markdown_table(metric_summary),
        "",
        "## Prior-Covered / Missing Subset Metrics",
        "",
        _markdown_table(_subset_summary(subset_rows)),
        "",
        "## Negative Controls",
        "",
        "`evoprior_additive_shuffled_gene_prior` and disabled gene-prior variants are included.",
        "",
        "## Limitations",
        "",
        "\n".join(f"- {item}" for item in config["reporting"].get("limitations", []))
        or "See claim boundary.",
        "",
    ]
    (run_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")


def _append_components(store, label: str, components: dict[str, pd.DataFrame]) -> None:
    slot = store.setdefault(label, {})
    for name, frame in components.items():
        slot.setdefault(name, []).append(frame)


def _concat_components(component_lists: dict[str, list[pd.DataFrame]]) -> dict[str, pd.DataFrame]:
    return {
        name: pd.concat(frames, axis=0)
        for name, frames in component_lists.items()
        if frames
    }


def _de_summary(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame()
    metric_columns = [
        column
        for column in frame.columns
        if column not in {"heldout", "baseline", "group_id"}
    ]
    return (
        frame.groupby("baseline", dropna=False)[metric_columns]
        .mean(numeric_only=True)
        .reset_index()
    )


def _subset_summary(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame()
    return (
        frame.groupby(["baseline", "subset"], dropna=False)[["mae_delta", "mse_delta", "n_genes"]]
        .mean(numeric_only=True)
        .reset_index()
    )


def _split_manifest(metadata: pd.DataFrame, split: pd.Series, heldout: str) -> pd.DataFrame:
    frame = metadata.copy()
    frame.insert(0, "group_id", frame.index.astype(str))
    frame.insert(1, "heldout", heldout)
    frame.insert(2, "split", split.astype(str).to_numpy())
    return frame.reset_index(drop=True)


def _load_lineage(config: dict[str, Any]) -> tuple[LineageTree, CellTypeLineageMapper]:
    tree = LineageTree.from_edges([(edge.get("parent"), edge["child"]) for edge in config["edges"]])
    return tree, CellTypeLineageMapper(config["cell_type_mapping"])


def _markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "No rows."
    columns = list(map(str, frame.columns))
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for _, row in frame.iterrows():
        lines.append("| " + " | ".join(str(row[column]) for column in frame.columns) + " |")
    return "\n".join(lines)


def _make_run_dir(config: dict[str, Any]) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return Path(config["output_root"]) / config["output_prefix"] / config["dataset_id"] / timestamp


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _write_yaml(path: Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=False, allow_unicode=True)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _git_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    main()
