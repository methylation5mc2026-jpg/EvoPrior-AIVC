"""Run the v0.13 GEARS-compatible Norman baseline benchmark."""

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
    NoChangeBaseline,
    PerturbationMeanDeltaBaselineV2,
    RidgeCVBaseline,
    SingleEffectAdditiveComboBaseline,
    build_delta_dataset,
)
from evoprior_aivc.data.download import prepare_dataset
from evoprior_aivc.data.gears_norman_adapter import (
    load_gears_norman_dataset,
    write_gears_norman_schema_report,
)
from evoprior_aivc.data.gears_splits import (
    assign_gears_compatible_combo_split,
    write_gears_split_report,
)
from evoprior_aivc.data.preprocess import preprocess_adata
from evoprior_aivc.data.pseudobulk import aggregate_pseudobulk
from evoprior_aivc.evaluation.benchmark_evidence import collect_run_evidence, write_evidence_outputs
from evoprior_aivc.evaluation.evaluator import evaluate_delta_predictions, subset_delta_dataset
from evoprior_aivc.evaluation.gears_metrics import (
    de_rows_for_dataset,
    per_class_metrics,
    per_perturbation_metrics,
)
from evoprior_aivc.evaluation.leakage_checks import assert_no_target_derived_features
from evoprior_aivc.evaluation.statistics import summarize_metric_table
from evoprior_aivc.models import EvoPriorAdditiveModel


def main() -> None:
    args = _parse_args()
    config = _load_yaml(Path(args.config))
    data_payload = _load_yaml(Path(config["data_config"]))
    data_config = data_payload["data"]
    preparation = prepare_dataset(data_config)
    run_dir = _make_run_dir(config)
    data_report_dir = Path("outputs/data_reports") / config["benchmark_id"] / run_dir.name
    run_dir.mkdir(parents=True, exist_ok=False)
    data_report_dir.mkdir(parents=True, exist_ok=True)
    _write_yaml(run_dir / "resolved_config.yaml", config)
    _write_yaml(run_dir / "resolved_data_config.yaml", data_payload)

    adata, schema_report = load_gears_norman_dataset(data_config, path=preparation.path)
    write_gears_norman_schema_report(schema_report, data_report_dir)
    write_gears_norman_schema_report(schema_report, run_dir)
    adata = preprocess_adata(adata, config)
    expression, metadata = aggregate_pseudobulk(
        adata,
        groupby=tuple(config["pseudobulk"]["groupby"]),
        layer=config["pseudobulk"].get("layer"),
        min_cells=int(config["pseudobulk"]["min_cells"]),
        aggregation=config["pseudobulk"]["aggregation"],
    )
    dataset = build_delta_dataset(
        expression,
        metadata,
        control_label=config["delta"]["control_label"],
        match_columns=tuple(config["delta"]["match_columns"]),
        fallback=config["delta"].get("control_fallback", "global"),
    )
    assert_no_target_derived_features(config["features"]["allowed_feature_columns"])
    split, split_manifest, split_audit = assign_gears_compatible_combo_split(
        dataset.metadata,
        seed=int(config["split"]["seed"]),
        seen_gene_fraction=float(config["split"]["seen_gene_fraction"]),
        test_combo_fraction=float(config["split"]["test_combo_fraction"]),
        val_fraction=float(config["split"]["val_fraction"]),
        min_test_combos_per_class=int(config["split"]["min_test_combos_per_class"]),
    )
    split_class_by_group = split_manifest.set_index("group_id")["split_class"]
    dataset.metadata["split_class"] = dataset.metadata.index.astype(str).map(split_class_by_group)
    split_manifest.to_csv(run_dir / "split_manifest.csv", index=False)
    split_manifest.to_csv(data_report_dir / "split_manifest.csv", index=False)
    write_gears_split_report(
        run_dir / "split_report.md",
        split_manifest=split_manifest,
        audit=split_audit,
    )
    write_gears_split_report(
        data_report_dir / "split_report.md",
        split_manifest=split_manifest,
        audit=split_audit,
    )

    metrics, per_pert, per_class, de_rows, fallback_frames = _evaluate(config, dataset, split)
    metric_summary = summarize_metric_table(
        metrics,
        group_columns=("split", "baseline"),
        metric_columns=tuple(config["evaluation"]["metric_columns"]),
    )
    per_class_summary = _summarize_per_class(per_class)
    de_summary = _summarize_de(de_rows)

    metrics.to_csv(run_dir / "metrics.csv", index=False)
    metrics.to_json(run_dir / "metrics.json", orient="records", indent=2)
    metric_summary.to_csv(run_dir / "metric_summary.csv", index=False)
    per_pert.to_csv(run_dir / "per_perturbation_metrics.csv", index=False)
    per_class.to_csv(run_dir / "per_class_metrics.csv", index=False)
    per_class_summary.to_csv(run_dir / "per_class_metric_summary.csv", index=False)
    de_rows.to_csv(run_dir / "de_metrics.csv", index=False)
    de_summary.to_csv(run_dir / "de_summary.csv", index=False)
    _concat_frames(fallback_frames).to_csv(run_dir / "combo_additive_fallbacks.csv", index=False)
    _write_json(run_dir / "dataset_preparation.json", preparation.to_dict())
    _write_json(run_dir / "schema_report.json", schema_report.__dict__)
    _write_json(run_dir / "split_leakage_audit.json", split_audit)
    _write_json(
        run_dir / "run_manifest.json",
        {
            "git_commit": _git_commit(),
            "experiment_id": config["experiment_id"],
            "benchmark_id": config["benchmark_id"],
            "dataset_id": config["dataset_id"],
            "command": (
                "python scripts/run_gears_norman_baseline.py --config "
                "configs/experiment/gears_norman_v013_baseline.yaml"
            ),
            "data_source": config["benchmark"]["source"],
            "data_checksum": data_config["dataset"]["checksum"],
            "split_definition": config["benchmark"]["split_definition"],
            "metric_script": "src/evoprior_aivc/evaluation/gears_metrics.py",
            "alignment_status": config["benchmark"]["official_alignment_status"],
            "claim_boundary": config["reporting"]["claim_boundary"],
        },
    )
    _write_report(
        run_dir,
        config=config,
        metric_summary=metric_summary,
        per_class_summary=per_class_summary,
        de_summary=de_summary,
        split_audit=split_audit,
        data_report_dir=data_report_dir,
        preparation=preparation.to_dict(),
    )
    records = collect_run_evidence(run_dir, config_path=args.config)
    write_evidence_outputs(records, run_dir, title="v0.13 GEARS/Norman Benchmark Evidence")
    print(run_dir)


def _evaluate(config: dict[str, Any], dataset, split: pd.Series):
    metric_rows: list[dict[str, Any]] = []
    per_perturbation_frames: list[pd.DataFrame] = []
    per_class_frames: list[pd.DataFrame] = []
    de_frames: list[pd.DataFrame] = []
    fallback_frames: list[pd.DataFrame] = []
    train = subset_delta_dataset(dataset, split == "train")
    for baseline in _baseline_instances(config["baselines"]):
        baseline.fit(train)
        for split_label in ("val", "test"):
            mask = split == split_label
            if not mask.any():
                continue
            query = subset_delta_dataset(dataset, mask)
            predicted = baseline.predict_delta(query)
            metrics = evaluate_delta_predictions(query, predicted)
            metric_rows.append(
                {
                    "split": split_label,
                    "baseline": baseline.name,
                    "n_examples": len(query.group_ids),
                    **metrics,
                }
            )
            per_pert = per_perturbation_metrics(query, predicted)
            per_pert.insert(0, "baseline", baseline.name)
            per_pert.insert(0, "split", split_label)
            per_perturbation_frames.append(per_pert)
            per_cls = per_class_metrics(query, predicted)
            per_cls.insert(0, "baseline", baseline.name)
            per_cls.insert(0, "split", split_label)
            per_class_frames.append(per_cls)
            de_frame = pd.DataFrame(
                de_rows_for_dataset(
                    query,
                    predicted,
                    ks=tuple(config["evaluation"]["de_ks"]),
                )
            )
            de_frame.insert(0, "baseline", baseline.name)
            de_frame.insert(0, "split", split_label)
            de_frames.append(de_frame)
            if hasattr(baseline, "prediction_fallbacks"):
                fallbacks = baseline.prediction_fallbacks()
                if not fallbacks.empty:
                    fallbacks.insert(0, "baseline", baseline.name)
                    fallbacks.insert(0, "split", split_label)
                    fallback_frames.append(fallbacks)
    return (
        pd.DataFrame(metric_rows),
        _concat_frames(per_perturbation_frames),
        _concat_frames(per_class_frames),
        _concat_frames(de_frames),
        fallback_frames,
    )


def _baseline_instances(configs: list[dict[str, Any]]):
    for config in configs:
        name = config["name"]
        if name == "no_change":
            yield NoChangeBaseline()
        elif name == "control_mean":
            yield ControlMeanBaseline()
        elif name == "mean_delta":
            yield MeanDeltaBaseline(fallback=config.get("fallback", "global"))
        elif name == "perturbation_mean_delta_v2":
            yield PerturbationMeanDeltaBaselineV2(fallback=config.get("fallback", "global"))
        elif name == "hierarchical_additive":
            yield HierarchicalAdditiveBaseline(alpha=float(config.get("alpha", 5.0)))
        elif name == "single_effect_additive_combo":
            yield SingleEffectAdditiveComboBaseline(
                missing_single_fallback=config.get(
                    "missing_single_fallback",
                    "global_single_mean",
                )
            )
        elif name == "ridge_cv":
            yield RidgeCVBaseline(alphas=tuple(map(float, config.get("alphas", [1.0]))))
        elif name == "evoprior_additive_no_prior":
            model = EvoPriorAdditiveModel(
                use_gene_prior=False,
                use_lineage_prior=False,
                alpha_shrinkage=float(config.get("alpha_shrinkage", 1.0)),
                min_groups_per_effect=int(config.get("min_groups_per_effect", 1)),
            )
            model.name = "evoprior_additive_no_prior"
            yield model
        else:
            raise ValueError(f"unsupported baseline: {name}")


def _summarize_per_class(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame
    metric_columns = ["mae_delta", "mse_delta", "pearson_delta", "spearman_logfc"]
    return (
        frame.groupby(["split", "baseline", "group_column", "group_value"], dropna=False)[
            metric_columns
        ]
        .mean(numeric_only=True)
        .reset_index()
    )


def _summarize_de(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame
    metric_columns = [
        column
        for column in frame.columns
        if column.startswith("top_") or column == "spearman_gene_rank"
    ]
    return (
        frame.groupby(["split", "baseline", "perturbation_type", "split_class"], dropna=False)[
            metric_columns
        ]
        .mean(numeric_only=True)
        .reset_index()
    )


def _write_report(
    run_dir: Path,
    *,
    config: dict[str, Any],
    metric_summary: pd.DataFrame,
    per_class_summary: pd.DataFrame,
    de_summary: pd.DataFrame,
    split_audit: dict[str, Any],
    data_report_dir: Path,
    preparation: dict[str, Any],
) -> None:
    lines = [
        "# v0.13 GEARS/Norman Baseline Run",
        "",
        "## Executive Summary",
        "",
        "A GEARS-compatible internal baseline run was executed on public Norman/scPerturb data.",
        "",
        "## Benchmark Alignment Status",
        "",
        f"- Status: `{config['benchmark']['official_alignment_status']}`",
        f"- Notes: {config['benchmark']['official_alignment_notes']}",
        "",
        "## Data Source And Checksum",
        "",
        f"- Source: {config['benchmark']['source']}",
        f"- Local path: `{preparation['path']}`",
        f"- Checksum status: `{preparation['checksum_status']}`",
        "",
        "## Schema Mapping",
        "",
        f"- Schema report path: `{data_report_dir / 'schema_report.md'}`",
        "",
        "## Split Design",
        "",
        f"- Split definition: {config['benchmark']['split_definition']}",
        "",
        "## Leakage Audit",
        "",
        f"- Passed: `{split_audit['overall_pass']}`",
        f"- Test combo leakage: `{split_audit['leaked_test_combos']}`",
        "",
        "## Baselines",
        "",
        "\n".join(f"- `{item['name']}`" for item in config["baselines"]),
        "",
        "## Main Metrics",
        "",
        _markdown_table(metric_summary),
        "",
        "## Combo Perturbation And Split-Class Metrics",
        "",
        _markdown_table(per_class_summary),
        "",
        "## DE20/DE50 Recovery",
        "",
        _markdown_table(de_summary),
        "",
        "## Failure Cases",
        "",
        "Inspect `per_perturbation_metrics.csv` and `combo_additive_fallbacks.csv`.",
        "",
        "## External Claim Boundary",
        "",
        config["reporting"]["claim_boundary"],
        "",
        "## Next Steps Toward Official GEARS/Leaderboard Comparability",
        "",
        "- Import exact official GEARS split files if available.",
        "- Match official GEARS preprocessing and metric scripts before leaderboard claims.",
        "- Compare against a true GEARS model only in a later neural-baseline milestone.",
        "",
    ]
    (run_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")


def _concat_frames(frames: list[pd.DataFrame]) -> pd.DataFrame:
    nonempty = [frame for frame in frames if not frame.empty]
    if not nonempty:
        return pd.DataFrame()
    columns = list(dict.fromkeys(column for frame in nonempty for column in frame.columns))
    rows = [record for frame in nonempty for record in frame.to_dict("records")]
    return pd.DataFrame.from_records(rows, columns=columns)


def _markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "No rows."
    columns = list(map(str, frame.columns))
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for _, row in frame.iterrows():
        cells = [_format_cell(row[column]) for column in frame.columns]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def _format_cell(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def _make_run_dir(config: dict[str, Any]) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return (
        Path(config["output_root"])
        / config["output_prefix"]
        / config["benchmark_id"]
        / timestamp
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    return payload if isinstance(payload, dict) else {}


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


if __name__ == "__main__":
    main()
