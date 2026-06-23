"""Run v0.5 lineage-prior synthetic and compatibility checks."""

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
from evoprior_aivc.data.synthetic_lineage import (
    CELL_TYPES,
    heldout_cell_type_split,
    make_synthetic_lineage_adata,
    make_synthetic_lineage_tree,
)
from evoprior_aivc.evaluation.de_metrics import de_recovery_metrics
from evoprior_aivc.evaluation.evaluator import evaluate_delta_predictions, subset_delta_dataset
from evoprior_aivc.evaluation.statistics import summarize_metric_table
from evoprior_aivc.priors.cell_lineage import LineageTree


def main() -> None:
    args = _parse_args()
    config = _load_yaml(Path(args.config))
    mode = config.get("mode", "synthetic_lineage")
    if mode == "synthetic_lineage":
        run_synthetic_lineage(config)
    elif mode == "real_compatibility":
        run_real_compatibility(config)
    else:
        raise ValueError(f"unsupported lineage runner mode: {mode}")


def run_synthetic_lineage(config: dict[str, Any]) -> Path:
    tree = make_synthetic_lineage_tree()
    adata = make_synthetic_lineage_adata(seed=config["seed"], **config["synthetic"])
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
    run_dir = _make_run_dir(config, dataset_id="synthetic_lineage")
    _write_yaml(run_dir / "resolved_config.yaml", config)
    _write_lineage_manifest(run_dir / "lineage_tree_edges.csv", tree)

    metric_rows: list[dict[str, Any]] = []
    de_rows: list[dict[str, Any]] = []
    split_rows: list[pd.DataFrame] = []
    for heldout in config["splits"]["heldout_cell_types"]:
        split = heldout_cell_type_split(dataset.metadata, heldout_cell_type=heldout)
        train = subset_delta_dataset(dataset, split == "train")
        test = subset_delta_dataset(dataset, split == "test")
        split_rows.append(
            pd.DataFrame(
                {
                    "heldout_cell_type": heldout,
                    "group_id": dataset.metadata.index,
                    "split": split.astype(str).to_numpy(),
                    "cell_type": dataset.metadata["cell_type"].to_numpy(),
                    "perturbation": dataset.metadata["perturbation"].to_numpy(),
                    "n_cells": dataset.metadata["n_cells"].to_numpy(),
                }
            )
        )
        for baseline in _baseline_instances(config, tree):
            baseline.fit(train)
            predicted = baseline.predict_delta(test)
            metrics = evaluate_delta_predictions(test, predicted)
            metric_rows.append(
                {
                    "experiment_id": config["experiment_id"],
                    "dataset_id": "synthetic_lineage",
                    "heldout_cell_type": heldout,
                    "baseline": baseline.name,
                    "split": "test",
                    "n_examples": len(test.group_ids),
                    **metrics,
                }
            )
            de_summary = _summarize_de_recovery(test.observed_delta, predicted, ks=(20, 50, 100))
            de_summary.update(
                {
                    "heldout_cell_type": heldout,
                    "baseline": baseline.name,
                    "split": "test",
                }
            )
            de_rows.append(de_summary)

    metrics_df = pd.DataFrame(metric_rows)
    ci_df = summarize_metric_table(
        metrics_df,
        group_columns=("baseline", "split"),
        metric_columns=("mae_delta", "mse_delta", "pearson_delta", "spearman_logfc"),
    )
    de_df = pd.DataFrame(de_rows)
    split_df = pd.concat(split_rows, ignore_index=True)
    metrics_df.to_csv(run_dir / "metrics.csv", index=False)
    ci_df.to_csv(run_dir / "metric_summary.csv", index=False)
    de_df.to_csv(run_dir / "de_summary.csv", index=False)
    split_df.to_csv(run_dir / "split_manifest.csv", index=False)
    _write_json(
        run_dir / "run_manifest.json",
        {
            "git_commit": _git_commit(),
            "claim_boundary": config["reporting"]["claim_boundary"],
            "cell_types": list(CELL_TYPES),
            "lineage_validation": "synthetic logic validation only",
        },
    )
    _write_synthetic_report(run_dir, config, metrics_df, ci_df, de_df)
    print(run_dir)
    return run_dir


def run_real_compatibility(config: dict[str, Any]) -> Path:
    prepare_dataset(config["data"])
    adata, schema_report = load_real_dataset(config["data"])
    adata = preprocess_adata(adata, config)
    unique_cell_types = sorted(map(str, adata.obs["cell_type"].unique()))
    tree = LineageTree.from_edges(
        [(None, "root")] + [("root", cell_type) for cell_type in unique_cell_types]
    )
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
    run_dir = _make_run_dir(config, dataset_id=config["dataset_id"])
    _write_yaml(run_dir / "resolved_config.yaml", config)
    _write_json(run_dir / "schema_report.json", schema_report.__dict__)
    baseline = LineageShrinkageBaseline(tree=tree, **_lineage_kwargs(config)).fit(dataset)
    predictions = baseline.predict_delta(dataset)
    metrics = evaluate_delta_predictions(dataset, predictions)
    metrics_df = pd.DataFrame(
        [
            {
                "experiment_id": config["experiment_id"],
                "dataset_id": config["dataset_id"],
                "baseline": baseline.name,
                "mode": "compatibility_noop",
                "n_cell_types": len(unique_cell_types),
                "is_noop": baseline.is_noop_,
                **metrics,
            }
        ]
    )
    metrics_df.to_csv(run_dir / "metrics.csv", index=False)
    _write_json(
        run_dir / "run_manifest.json",
        {
            "git_commit": _git_commit(),
            "unique_cell_types": unique_cell_types,
            "claim_boundary": config["reporting"]["claim_boundary"],
            "conclusion": "lineage signal is not identifiable with one cell type",
        },
    )
    _write_papalexi_report(run_dir, config, metrics_df, unique_cell_types)
    print(run_dir)
    return run_dir


def _baseline_instances(config: dict[str, Any], tree):
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
            yield LineageShrinkageBaseline(tree=tree, **_lineage_kwargs(config))
        else:
            raise ValueError(f"unsupported baseline: {name}")


def _lineage_kwargs(config: dict[str, Any]) -> dict[str, Any]:
    raw = config["lineage_baseline"]
    return {
        "tau": float(raw.get("tau", 1.0)),
        "shrinkage": float(raw.get("shrinkage", 0.8)),
        "fallback_mode": raw.get("fallback_mode", "global"),
    }


def _summarize_de_recovery(
    observed: pd.DataFrame,
    predicted: pd.DataFrame,
    *,
    ks: tuple[int, ...],
) -> dict[str, object]:
    rows = []
    predicted = predicted.loc[observed.index, observed.columns]
    for group_id in observed.index:
        rows.append(
            de_recovery_metrics(
                observed.loc[group_id].to_numpy(dtype=float),
                predicted.loc[group_id].to_numpy(dtype=float),
                ks=ks,
            )
        )
    frame = pd.DataFrame(rows)
    return {column: frame[column].mean(skipna=True) for column in frame.columns}


def _write_synthetic_report(run_dir: Path, config: dict[str, Any], metrics, ci, de) -> None:
    lines = [
        "# v0.5 Synthetic Lineage Prior Report",
        "",
        (
            "This is a synthetic sanity benchmark designed to validate lineage-prior "
            "plumbing and expected behavior under known lineage-structured response "
            "generation. It does not prove biological improvement on real data."
        ),
        "",
        "## Claim Boundary",
        "",
        config["reporting"]["claim_boundary"],
        "",
        "## Metric Summary",
        "",
        _markdown_table(ci),
        "",
        "## Raw Metrics",
        "",
        _markdown_table(metrics),
        "",
        "## DE Recovery Summary",
        "",
        _markdown_table(de),
        "",
        "## Limitations",
        "",
        (
            "- Synthetic response generation is intentionally structured and may be "
            "easier than real biology."
        ),
        "- This run does not validate lineage priors on a real multi-cell-type dataset.",
        "- No neural EvoPrior model is implemented.",
        "",
    ]
    (run_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")


def _write_papalexi_report(
    run_dir: Path,
    config: dict[str, Any],
    metrics,
    cell_types: list[str],
) -> None:
    lines = [
        "# v0.5 Papalexi Lineage Compatibility Report",
        "",
        (
            "Papalexi is useful for real-data plumbing but not suitable for evaluating "
            "cell-lineage priors because it contains only one cell type/cell line in "
            "the current setup."
        ),
        "",
        "## Claim Boundary",
        "",
        config["reporting"]["claim_boundary"],
        "",
        "## Observed Cell Types",
        "",
        ", ".join(cell_types),
        "",
        "## Compatibility Metrics",
        "",
        _markdown_table(metrics),
        "",
        "## Conclusion",
        "",
        (
            "Lineage signal is not identifiable on this dataset. The lineage baseline "
            "ran in safe fallback/no-op mode."
        ),
        "",
    ]
    (run_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")


def _write_lineage_manifest(path: Path, tree) -> None:
    rows = []
    for node in tree.nodes:
        rows.append({"node": node, "parent": tree.parent(node), "depth": tree.depth(node)})
    pd.DataFrame(rows).to_csv(path, index=False)


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


def _make_run_dir(config: dict[str, Any], *, dataset_id: str) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = Path(config["output_root"]) / config["output_prefix"] / dataset_id / timestamp
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


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
