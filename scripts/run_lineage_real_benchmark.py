"""Run the v0.6 real multi-cell-type lineage benchmark."""

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
    HierarchicalAdditiveBaseline,
    MeanDeltaBaseline,
    PerturbationMeanDeltaBaselineV2,
    RidgeCVBaseline,
    build_delta_dataset,
)
from evoprior_aivc.baselines.lineage_shrinkage import LineageShrinkageBaseline
from evoprior_aivc.data.download import prepare_dataset
from evoprior_aivc.data.preprocess import preprocess_adata
from evoprior_aivc.data.pseudobulk import aggregate_pseudobulk
from evoprior_aivc.data.real_loader import load_real_dataset
from evoprior_aivc.data.registry import DatasetRecord
from evoprior_aivc.data.splits import (
    assign_heldout_cell_type_split,
    assign_heldout_lineage_split,
    heldout_cell_type_eligibility,
)
from evoprior_aivc.evaluation.de_metrics import de_recovery_metrics
from evoprior_aivc.evaluation.evaluator import evaluate_delta_predictions, subset_delta_dataset
from evoprior_aivc.evaluation.leakage_checks import (
    assert_no_heldout_cell_type_target_leakage,
    assert_no_target_derived_features,
    assert_required_split_labels,
)
from evoprior_aivc.evaluation.statistics import summarize_metric_table
from evoprior_aivc.priors.cell_lineage import CellTypeLineageMapper, LineageTree


def main() -> None:
    args = _parse_args()
    config = _load_yaml(Path(args.config))
    run_dir = _make_run_dir(config)
    run_dir.mkdir(parents=True, exist_ok=False)
    _write_yaml(run_dir / "resolved_config.yaml", config)

    data_config = _load_yaml(Path(config["data_config"]))
    lineage_config = _load_yaml(Path(config["lineage_config"]))
    _write_yaml(run_dir / "resolved_data_config.yaml", data_config)
    _write_yaml(run_dir / "resolved_lineage_config.yaml", lineage_config)

    preparation = prepare_dataset(data_config)
    schema_dir = _make_schema_report_dir(data_config)
    adata, schema_report = load_real_dataset(data_config, schema_report_dir=schema_dir)
    adata = preprocess_adata(adata, config)
    expression, pseudobulk_metadata = aggregate_pseudobulk(
        adata,
        groupby=tuple(config["pseudobulk"]["groupby"]),
        min_cells=int(config["pseudobulk"]["min_cells"]),
        aggregation=config["pseudobulk"]["aggregation"],
    )
    dataset = build_delta_dataset(
        expression,
        pseudobulk_metadata,
        control_label=config["delta"]["control_label"],
        match_columns=tuple(config["delta"]["match_columns"]),
        fallback=config["delta"].get("control_fallback", "raise"),
    )
    assert_no_target_derived_features(config["features"]["allowed_feature_columns"])

    tree, mapper = _load_lineage(lineage_config)
    lineage_report = _lineage_mapping_report(lineage_config, tree, mapper, pseudobulk_metadata)
    (run_dir / "lineage_mapping_report.md").write_text(lineage_report, encoding="utf-8")

    coverage = _pseudobulk_coverage(pseudobulk_metadata, config["delta"]["control_label"])
    coverage.to_csv(run_dir / "pseudobulk_coverage.csv", index=False)
    pseudobulk_metadata.to_csv(run_dir / "pseudobulk_metadata.csv", index=True)

    suite = config["splits"]["heldout_cell_type_suite"]
    eligibility = heldout_cell_type_eligibility(
        pseudobulk_metadata,
        control_label=config["delta"]["control_label"],
        min_test_groups=int(suite["min_test_groups"]),
        min_control_groups=int(suite["min_control_groups"]),
        min_train_groups=int(suite["min_train_groups"]),
    )
    eligibility.to_csv(run_dir / "heldout_cell_type_eligibility.csv", index=False)

    metric_rows: list[dict[str, Any]] = []
    de_rows: list[dict[str, Any]] = []
    split_frames: list[pd.DataFrame] = []
    skipped_rows: list[dict[str, Any]] = []

    if suite.get("enabled", True):
        _run_cell_type_suite(
            config,
            dataset,
            tree,
            mapper,
            eligibility,
            metric_rows,
            de_rows,
            split_frames,
            skipped_rows,
        )

    lineage_suite = config["splits"]["heldout_lineage_suite"]
    if lineage_suite.get("enabled", True):
        _run_lineage_suite(
            config,
            dataset,
            tree,
            lineage_config,
            metric_rows,
            de_rows,
            split_frames,
            skipped_rows,
        )

    if not metric_rows:
        raise RuntimeError("no eligible v0.6 splits produced metrics")

    metrics = pd.DataFrame(metric_rows)
    de_metrics = pd.DataFrame(de_rows)
    split_manifest = pd.concat(split_frames, ignore_index=True) if split_frames else pd.DataFrame()
    skipped = pd.DataFrame(skipped_rows)
    metric_summary = summarize_metric_table(
        metrics,
        group_columns=("split_mode", "split", "baseline"),
        metric_columns=tuple(config["evaluation"]["metric_columns"]),
    )
    de_summary = _summarize_de_table(de_metrics)
    retrieval_summary = pd.DataFrame(
        [
            {
                "status": "skipped",
                "reason": config["evaluation"]["retrieval_pds"]["reason"],
            }
        ]
    )

    metrics.to_csv(run_dir / "metrics.csv", index=False)
    metric_summary.to_csv(run_dir / "metric_summary.csv", index=False)
    de_metrics.to_csv(run_dir / "de_metrics.csv", index=False)
    de_summary.to_csv(run_dir / "de_summary.csv", index=False)
    split_manifest.to_csv(run_dir / "split_manifest.csv", index=False)
    skipped.to_csv(run_dir / "skipped_cell_types_and_lineages.csv", index=False)
    retrieval_summary.to_csv(run_dir / "retrieval_pds_summary.csv", index=False)
    _write_json(run_dir / "dataset_preparation.json", preparation.to_dict())
    _write_json(run_dir / "dataset_registry.json", DatasetRecord.from_config(data_config).to_dict())
    _write_json(run_dir / "schema_report.json", schema_report.__dict__)
    _write_json(
        run_dir / "run_manifest.json",
        {
            "git_commit": _git_commit(),
            "dataset_id": config["dataset_id"],
            "experiment_id": config["experiment_id"],
            "schema_report_dir": str(schema_dir),
            "control_usage": config["splits"]["control_usage"],
            "claim_boundary": config["reporting"]["claim_boundary"],
            "n_metric_rows": int(metrics.shape[0]),
            "n_eligible_cell_types": int(eligibility["eligible"].sum()),
            "retrieval_pds": "skipped_single_non_control_perturbation",
        },
    )
    _write_report(
        run_dir,
        config,
        schema_report,
        lineage_config,
        eligibility,
        metric_summary,
        metrics,
        de_summary,
        skipped,
    )
    print(run_dir)


def _run_cell_type_suite(
    config: dict[str, Any],
    dataset,
    tree: LineageTree,
    mapper: CellTypeLineageMapper,
    eligibility: pd.DataFrame,
    metric_rows: list[dict[str, Any]],
    de_rows: list[dict[str, Any]],
    split_frames: list[pd.DataFrame],
    skipped_rows: list[dict[str, Any]],
) -> None:
    suite = config["splits"]["heldout_cell_type_suite"]
    for _, row in eligibility.iterrows():
        heldout = str(row["cell_type"])
        if not bool(row["eligible"]):
            skipped_rows.append(
                {
                    "split_mode": "heldout_cell_type_suite",
                    "heldout": heldout,
                    "reason": row["reason"],
                }
            )
            continue
        split = assign_heldout_cell_type_split(
            dataset.metadata,
            heldout_cell_type=heldout,
            val_fraction=float(suite["val_fraction"]),
            seed=int(suite["seed"]),
        )
        assert_required_split_labels(split, required_labels=("train", "test"))
        assert_no_heldout_cell_type_target_leakage(
            dataset.metadata,
            split,
            heldout_cell_type=heldout,
            control_usage=config["splits"]["control_usage"],
        )
        split_frames.append(
            _split_manifest(dataset.metadata, split, "heldout_cell_type_suite", heldout)
        )
        _evaluate_split(
            config,
            dataset,
            split,
            tree,
            mapper,
            split_mode="heldout_cell_type_suite",
            heldout=heldout,
            metric_rows=metric_rows,
            de_rows=de_rows,
        )


def _run_lineage_suite(
    config: dict[str, Any],
    dataset,
    tree: LineageTree,
    lineage_config: dict[str, Any],
    metric_rows: list[dict[str, Any]],
    de_rows: list[dict[str, Any]],
    split_frames: list[pd.DataFrame],
    skipped_rows: list[dict[str, Any]],
) -> None:
    suite = config["splits"]["heldout_lineage_suite"]
    mapper = CellTypeLineageMapper(lineage_config["cell_type_mapping"])
    for clade in suite["candidate_clades"]:
        heldout_cell_types = _cell_types_in_clade(lineage_config, tree, str(clade))
        test_mask = dataset.metadata["cell_type"].isin(heldout_cell_types)
        train_mask = ~test_mask
        reason = _lineage_split_skip_reason(
            dataset,
            test_mask,
            train_mask,
            min_test_groups=int(suite["min_test_groups"]),
            min_train_groups=int(suite["min_train_groups"]),
        )
        if reason is not None:
            skipped_rows.append(
                {
                    "split_mode": "heldout_lineage_suite",
                    "heldout": str(clade),
                    "reason": reason,
                }
            )
            continue
        split = assign_heldout_lineage_split(
            dataset.metadata,
            heldout_cell_types=heldout_cell_types,
            val_fraction=float(suite["val_fraction"]),
            seed=int(suite["seed"]),
        )
        assert_required_split_labels(split, required_labels=("train", "test"))
        split_frames.append(
            _split_manifest(dataset.metadata, split, "heldout_lineage_suite", str(clade))
        )
        _evaluate_split(
            config,
            dataset,
            split,
            tree,
            mapper,
            split_mode="heldout_lineage_suite",
            heldout=str(clade),
            metric_rows=metric_rows,
            de_rows=de_rows,
        )


def _evaluate_split(
    config: dict[str, Any],
    dataset,
    split: pd.Series,
    tree: LineageTree,
    mapper: CellTypeLineageMapper,
    *,
    split_mode: str,
    heldout: str,
    metric_rows: list[dict[str, Any]],
    de_rows: list[dict[str, Any]],
) -> None:
    train = subset_delta_dataset(dataset, split == "train")
    test = subset_delta_dataset(dataset, split == "test")
    for baseline in _baseline_instances(config, tree, mapper):
        baseline.fit(train)
        predicted = baseline.predict_delta(test)
        metrics = evaluate_delta_predictions(test, predicted)
        metric_rows.append(
            {
                "experiment_id": config["experiment_id"],
                "dataset_id": config["dataset_id"],
                "split_mode": split_mode,
                "split": "test",
                "heldout": heldout,
                "baseline": baseline.name,
                "n_train_examples": len(train.group_ids),
                "n_test_examples": len(test.group_ids),
                **metrics,
            }
        )
        for group_id in test.group_ids:
            row = de_recovery_metrics(
                test.observed_delta.loc[group_id].to_numpy(dtype=float),
                predicted.loc[group_id].to_numpy(dtype=float),
                ks=tuple(config["evaluation"]["de_ks"]),
            )
            row.update(
                {
                    "split_mode": split_mode,
                    "heldout": heldout,
                    "baseline": baseline.name,
                    "group_id": group_id,
                }
            )
            de_rows.append(row)


def _baseline_instances(
    config: dict[str, Any],
    tree: LineageTree,
    mapper: CellTypeLineageMapper,
):
    for item in config["baselines"]:
        name = item["name"]
        if name == "control_mean":
            yield ControlMeanBaseline()
        elif name == "mean_delta":
            yield MeanDeltaBaseline(fallback=item.get("fallback", "global"))
        elif name == "perturbation_mean_delta_v2":
            yield PerturbationMeanDeltaBaselineV2(fallback=item.get("fallback", "global"))
        elif name == "hierarchical_additive":
            yield HierarchicalAdditiveBaseline(alpha=float(item.get("alpha", 5.0)))
        elif name == "ridge_cv":
            yield RidgeCVBaseline(alphas=tuple(item.get("alphas", [0.1, 1.0, 10.0])))
        elif name == "lineage_shrinkage":
            raw = config["lineage_baseline"]
            baseline = LineageShrinkageBaseline(
                tree=tree,
                mapper=mapper,
                tau=float(item.get("tau", raw.get("tau", 1.0))),
                shrinkage=float(item.get("shrinkage", raw.get("shrinkage", 0.8))),
                fallback_mode=item.get("fallback_mode", raw.get("fallback_mode", "global")),
            )
            if "label" in item:
                baseline.name = str(item["label"])
            yield baseline
        else:
            raise ValueError(f"unsupported baseline: {name}")


def _load_lineage(config: dict[str, Any]) -> tuple[LineageTree, CellTypeLineageMapper]:
    edges = [(edge.get("parent"), edge["child"]) for edge in config["edges"]]
    tree = LineageTree.from_edges(edges)
    mapper = CellTypeLineageMapper(config["cell_type_mapping"])
    return tree, mapper


def _cell_types_in_clade(
    config: dict[str, Any],
    tree: LineageTree,
    clade: str,
) -> list[str]:
    descendants = set(tree.descendants(clade, include_self=True))
    return sorted(
        cell_type
        for cell_type, node in config["cell_type_mapping"].items()
        if node in descendants
    )


def _lineage_split_skip_reason(
    dataset,
    test_mask: pd.Series,
    train_mask: pd.Series,
    *,
    min_test_groups: int,
    min_train_groups: int,
) -> str | None:
    if int(test_mask.sum()) < min_test_groups:
        return "too_few_test_groups"
    if int(train_mask.sum()) < min_train_groups:
        return "too_few_train_groups"
    if not set(dataset.metadata.loc[test_mask, "perturbation"]).intersection(
        set(dataset.metadata.loc[train_mask, "perturbation"])
    ):
        return "no_train_overlap_for_heldout_perturbations"
    return None


def _pseudobulk_coverage(metadata: pd.DataFrame, control_label: str) -> pd.DataFrame:
    rows = []
    grouped = metadata.groupby(["cell_type", "perturbation"], observed=True)
    for (cell_type, perturbation), group in grouped:
        rows.append(
            {
                "cell_type": cell_type,
                "perturbation": perturbation,
                "n_groups": int(group.shape[0]),
                "n_cells_total": int(group["n_cells"].sum()),
                "is_control": perturbation == control_label,
            }
        )
    return pd.DataFrame(rows).sort_values(["cell_type", "perturbation"], kind="mergesort")


def _lineage_mapping_report(
    config: dict[str, Any],
    tree: LineageTree,
    mapper: CellTypeLineageMapper,
    pseudobulk_metadata: pd.DataFrame,
) -> str:
    observed = sorted(map(str, pseudobulk_metadata["cell_type"].unique()))
    unmapped = mapper.unmapped(observed)
    rows = [
        "| cell_type | lineage_node | depth |",
        "| --- | --- | --- |",
    ]
    for cell_type in observed:
        node = mapper.map_one(cell_type)
        rows.append(f"| {cell_type} | {node} | {tree.depth(node)} |")
    return "\n".join(
        [
            "# v0.6 Lineage Mapping Report",
            "",
            f"- Lineage ID: `{config['lineage_id']}`",
            f"- Dataset ID: `{config['dataset_id']}`",
            f"- Tree root: `{tree.root}`",
            f"- Nodes: {len(tree.nodes)}",
            f"- Max depth: {tree.validate().max_depth}",
            f"- Unmapped observed cell types: {', '.join(unmapped) if unmapped else 'none'}",
            "",
            config["claim_boundary"],
            "",
            "## Mapping",
            "",
            *rows,
            "",
        ]
    )


def _split_manifest(
    metadata: pd.DataFrame,
    split: pd.Series,
    split_mode: str,
    heldout: str,
) -> pd.DataFrame:
    frame = metadata.copy()
    frame.insert(0, "group_id", frame.index.astype(str))
    frame.insert(1, "split_mode", split_mode)
    frame.insert(2, "heldout", heldout)
    frame.insert(3, "split", split.astype(str).to_numpy())
    return frame.reset_index(drop=True)


def _summarize_de_table(de_metrics: pd.DataFrame) -> pd.DataFrame:
    if de_metrics.empty:
        return pd.DataFrame()
    metric_columns = [
        column
        for column in de_metrics.columns
        if column
        not in {
            "split_mode",
            "heldout",
            "baseline",
            "group_id",
        }
    ]
    return (
        de_metrics.groupby(["split_mode", "baseline"], dropna=False)[metric_columns]
        .mean(numeric_only=True)
        .reset_index()
    )


def _write_report(
    run_dir: Path,
    config: dict[str, Any],
    schema_report,
    lineage_config: dict[str, Any],
    eligibility: pd.DataFrame,
    metric_summary: pd.DataFrame,
    metrics: pd.DataFrame,
    de_summary: pd.DataFrame,
    skipped: pd.DataFrame,
) -> None:
    lines = [
        "# v0.6 Real Multi-Cell-Type Lineage Benchmark Report",
        "",
        "## Executive Summary",
        "",
        (
            "Kang 2018 PBMC IFN-beta was evaluated under documented held-out "
            "cell-type and coarse held-out-lineage splits. The benchmark compares "
            "v0.4 classical baselines with the v0.5 non-neural lineage shrinkage baseline."
        ),
        "",
        "## Claim Boundary",
        "",
        config["reporting"]["claim_boundary"],
        "",
        "## Dataset Selection and Suitability Gate",
        "",
        "See `docs/V06_REAL_MULTICELL_DATASET_SELECTION.md`.",
        "",
        "## Schema Mapping",
        "",
        (
            f"Cells: {schema_report.n_cells}; genes: {schema_report.n_genes}; "
            f"cell types: {schema_report.n_cell_types}; perturbations: "
            f"{schema_report.n_perturbations}; controls: {schema_report.n_controls}."
        ),
        "",
        "## Lineage Mapping",
        "",
        f"Lineage config: `{lineage_config['lineage_id']}`.",
        "",
        "## Pseudobulk and Controls",
        "",
        (
            "Pseudobulk grouping uses cell_type, perturbation, and donor. The main "
            "control policy is control-observed OOD: held-out cell-type controls are "
            "allowed as input control states, but held-out stimulated deltas are test-only."
        ),
        "",
        "## Split Design",
        "",
        _markdown_table(eligibility),
        "",
        "## Leakage Checks",
        "",
        "All evaluated held-out cell-type target deltas are absent from train/validation.",
        "",
        "## Baselines",
        "",
        ", ".join(item["name"] for item in config["baselines"]),
        "",
        "## Metrics",
        "",
        _markdown_table(metric_summary),
        "",
        "## Held-out Cell-Type Results",
        "",
        _markdown_table(metrics[metrics["split_mode"] == "heldout_cell_type_suite"]),
        "",
        "## Held-out Lineage Results",
        "",
        _markdown_table(metrics[metrics["split_mode"] == "heldout_lineage_suite"]),
        "",
        "## DE Recovery",
        "",
        _markdown_table(de_summary),
        "",
        "## Retrieval/PDS",
        "",
        config["evaluation"]["retrieval_pds"]["reason"],
        "",
        "## Sensitivity or Tau Audit",
        "",
        "Skipped in the main run; tau is pre-specified in the config.",
        "",
        "## Failure Cases",
        "",
        _markdown_table(skipped),
        "",
        "## Limitations",
        "",
        *_list_lines(config["reporting"]["limitations"]),
        "",
        "## What This Enables For v0.7",
        "",
        (
            "The project can now add a gene-level evolutionary/conservation prior "
            "on top of a real multi-cell-type benchmark substrate."
        ),
        "",
    ]
    (run_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")


def _markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "No rows."
    columns = list(map(str, frame.columns))
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for _, row in frame.iterrows():
        lines.append(
            "| " + " | ".join(_format_cell(row[column]) for column in frame.columns) + " |"
        )
    return "\n".join(lines)


def _format_cell(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def _list_lines(items: list[str]) -> list[str]:
    return [f"- {item}" for item in items] if items else ["- none"]


def _make_run_dir(config: dict[str, Any]) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return Path(config["output_root"]) / config["output_prefix"] / config["dataset_id"] / timestamp


def _make_schema_report_dir(data_config: dict[str, Any]) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return Path("outputs/data_reports") / data_config["dataset"]["dataset_id"] / timestamp


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
