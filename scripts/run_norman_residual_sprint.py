"""Run the v0.16 Norman residual model-improvement sprint."""

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
    ResidualComboConfig,
    ResidualComboCorrectionBaseline,
    SingleEffectAdditiveComboBaseline,
    WeightedComboAdditiveBaseline,
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
from evoprior_aivc.evaluation.evaluator import evaluate_delta_predictions, subset_delta_dataset
from evoprior_aivc.evaluation.gears_metrics import (
    de_rows_for_dataset,
    per_class_metrics,
    per_perturbation_metrics,
)
from evoprior_aivc.evaluation.leakage_checks import assert_no_target_derived_features


def main() -> None:
    args = _parse_args()
    config = _load_yaml(Path(args.config))
    config["config_path"] = args.config
    data_payload = _load_yaml(Path(config["data_config"]))
    data_config = data_payload["data"]
    preparation = prepare_dataset(data_config)
    run_dir = _make_run_dir(config)
    data_report_dir = Path("outputs/data_reports") / config["benchmark_id"] / run_dir.name
    run_dir.mkdir(parents=True, exist_ok=False)
    data_report_dir.mkdir(parents=True, exist_ok=True)
    _write_yaml(run_dir / "resolved_config.yaml", config)
    _write_yaml(run_dir / "resolved_data_config.yaml", data_payload)

    dataset, split, split_manifest, split_audit, schema_report = _prepare_dataset(
        config,
        data_config,
        preparation.path,
    )
    write_gears_norman_schema_report(schema_report, data_report_dir)
    write_gears_norman_schema_report(schema_report, run_dir)
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
    _write_leakage_markdown(run_dir / "leakage_audit.md", split_audit)

    train = subset_delta_dataset(dataset, split == "train")
    val = subset_delta_dataset(dataset, split == config["selection"]["split"])
    test = subset_delta_dataset(dataset, split == "test")
    reference_metrics = _evaluate_references(config, train, val, test)
    sweep_rows, fitted_candidates = _validation_sweep(config, train, val)
    validation_sweep = pd.DataFrame(sweep_rows).sort_values("candidate_id")
    selected_row = _select_candidate(validation_sweep, config)
    selected_id = str(selected_row["candidate_id"])
    selected_model = fitted_candidates[selected_id]
    selected_config = selected_model.manifest()

    final_metrics, per_pert, per_class, de_metrics = _evaluate_final(
        selected_model,
        selected_id=selected_id,
        dataset=test,
        de_ks=tuple(config["evaluation"]["de_ks"]),
    )
    comparison = _comparison_table(config, reference_metrics, final_metrics)
    per_class_summary = _per_class_summary(per_class)
    de_summary = _de_summary(de_metrics)

    validation_sweep.to_csv(run_dir / "validation_sweep.csv", index=False)
    _write_yaml(run_dir / "selected_config.yaml", selected_config)
    pd.DataFrame([final_metrics]).to_csv(run_dir / "final_test_metrics.csv", index=False)
    reference_metrics.to_csv(run_dir / "reference_metrics.csv", index=False)
    per_pert.to_csv(run_dir / "per_perturbation_metrics.csv", index=False)
    per_class.to_csv(run_dir / "per_class_metrics.csv", index=False)
    per_class_summary.to_csv(run_dir / "per_class_metric_summary.csv", index=False)
    de_metrics.to_csv(run_dir / "de_metrics.csv", index=False)
    de_summary.to_csv(run_dir / "de_metric_summary.csv", index=False)
    comparison.to_csv(run_dir / "comparison_to_v014_v015.csv", index=False)
    _write_json(
        run_dir / "prediction_manifest.json",
        {
            "selected_candidate": selected_id,
            "predictions_materialized": False,
            "reason": "v0.16 records metrics and manifests without committing large predictions.",
            "final_test_metrics": "final_test_metrics.csv",
            "per_perturbation_metrics": "per_perturbation_metrics.csv",
        },
    )
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
                "python scripts/run_norman_residual_sprint.py --config "
                f"{config.get('config_path')}"
            ),
            "data_checksum": data_config["dataset"]["checksum"],
            "split_definition": config["benchmark"]["split_definition"],
            "metric_script": "src/evoprior_aivc/evaluation/gears_metrics.py",
            "selected_candidate": selected_id,
            "claim_boundary": config["reporting"]["claim_boundary"],
        },
    )
    _write_report(
        run_dir,
        config=config,
        validation_sweep=validation_sweep,
        selected_row=selected_row,
        final_metrics=final_metrics,
        comparison=comparison,
        per_class_summary=per_class_summary,
        de_summary=de_summary,
        split_audit=split_audit,
        data_report_dir=data_report_dir,
        preparation=preparation.to_dict(),
    )
    print(run_dir)
    print(selected_id)


def _prepare_dataset(config: dict[str, Any], data_config: dict[str, Any], path: str | Path):
    adata, schema_report = load_gears_norman_dataset(data_config, path=path)
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
        random_combo_fraction=float(config["split"].get("random_combo_fraction", 0.0)),
        val_fraction=float(config["split"]["val_fraction"]),
        min_test_combos_per_class=int(config["split"]["min_test_combos_per_class"]),
    )
    split_class_by_group = split_manifest.set_index("group_id")["split_class"]
    dataset.metadata["split_class"] = dataset.metadata.index.astype(str).map(split_class_by_group)
    return dataset, split, split_manifest, split_audit, schema_report


def _evaluate_references(config: dict[str, Any], train, val, test) -> pd.DataFrame:
    rows = []
    for baseline in _reference_baselines(config["reference_baselines"]):
        baseline.fit(train)
        for split_label, dataset in (("val", val), ("test", test)):
            predicted = baseline.predict_delta(dataset)
            rows.append(
                {
                    "candidate_id": baseline.name,
                    "split": split_label,
                    "model_family": "reference",
                    "n_examples": len(dataset.group_ids),
                    **evaluate_delta_predictions(dataset, predicted),
                }
            )
    return pd.DataFrame(rows)


def _validation_sweep(config: dict[str, Any], train, val):
    rows = []
    fitted = {}
    for item in config["candidate_models"]:
        candidate_id = str(item["candidate_id"])
        model = ResidualComboCorrectionBaseline(_residual_config(item))
        model.fit(train)
        predicted = model.predict_delta(val)
        metrics = evaluate_delta_predictions(val, predicted)
        row = {
            "candidate_id": candidate_id,
            "split": "val",
            "model_family": "residual_combo",
            "n_examples": len(val.group_ids),
            **_candidate_record(item),
            **metrics,
        }
        rows.append(row)
        fitted[candidate_id] = model
    return rows, fitted


def _select_candidate(validation_sweep: pd.DataFrame, config: dict[str, Any]) -> pd.Series:
    metric = config["selection"]["metric"]
    ascending = config["selection"].get("mode", "minimize") == "minimize"
    sort_columns = [metric]
    ascending_flags = [ascending]
    if "mse_delta" in validation_sweep.columns:
        sort_columns.append("mse_delta")
        ascending_flags.append(True)
    if "pearson_delta" in validation_sweep.columns:
        sort_columns.append("pearson_delta")
        ascending_flags.append(False)
    return validation_sweep.sort_values(sort_columns, ascending=ascending_flags).iloc[0]


def _evaluate_final(model, *, selected_id: str, dataset, de_ks: tuple[int, ...]):
    predicted = model.predict_delta(dataset)
    metrics = {
        "candidate_id": selected_id,
        "split": "test",
        "model_family": "residual_combo_selected",
        "n_examples": len(dataset.group_ids),
        **evaluate_delta_predictions(dataset, predicted),
    }
    per_pert = per_perturbation_metrics(dataset, predicted)
    per_pert.insert(0, "candidate_id", selected_id)
    per_pert.insert(0, "split", "test")
    per_class = per_class_metrics(dataset, predicted)
    per_class.insert(0, "candidate_id", selected_id)
    per_class.insert(0, "split", "test")
    de_frame = pd.DataFrame(de_rows_for_dataset(dataset, predicted, ks=de_ks))
    de_frame.insert(0, "candidate_id", selected_id)
    de_frame.insert(0, "split", "test")
    return metrics, per_pert, per_class, de_frame


def _comparison_table(
    config: dict[str, Any],
    reference_metrics: pd.DataFrame,
    final_metrics: dict[str, Any],
) -> pd.DataFrame:
    rows = []
    for row in config["comparison_reference"]["rows"]:
        rows.append({"label": row["label"], "source": "historical", **row})
    test_refs = reference_metrics[reference_metrics["split"] == "test"]
    for _, row in test_refs.iterrows():
        rows.append(
            {
                "label": f"v0.16_recomputed_{row['candidate_id']}",
                "source": "recomputed",
                **_metric_subset(row),
            }
        )
    rows.append(
        {
            "label": f"v0.16_selected_{final_metrics['candidate_id']}",
            "source": "selected",
            **_metric_subset(final_metrics),
        }
    )
    frame = pd.DataFrame(rows)
    weighted = _lookup_metric(frame, "v0.14_weighted_combo_additive")
    single = _lookup_metric(frame, "v0.14_single_effect_additive_combo")
    frame["beats_v014_weighted_mae"] = frame["mae_delta"] < weighted["mae_delta"]
    frame["beats_v014_weighted_mse"] = frame["mse_delta"] < weighted["mse_delta"]
    frame["beats_v014_single_pearson"] = frame["pearson_delta"] > single["pearson_delta"]
    frame["beats_v014_single_spearman"] = frame["spearman_logfc"] > single["spearman_logfc"]
    return frame


def _reference_baselines(configs: list[dict[str, Any]]):
    for config in configs:
        name = config["name"]
        if name == "single_effect_additive_combo":
            yield SingleEffectAdditiveComboBaseline(
                missing_single_fallback=config.get(
                    "missing_single_fallback",
                    "global_single_mean",
                )
            )
        elif name == "weighted_combo_additive":
            yield WeightedComboAdditiveBaseline(
                ridge_alpha=float(config.get("ridge_alpha", 1.0)),
                missing_single_fallback=config.get(
                    "missing_single_fallback",
                    "global_single_mean",
                ),
            )
        else:
            raise ValueError(f"unsupported reference baseline: {name}")


def _residual_config(item: dict[str, Any]) -> ResidualComboConfig:
    return ResidualComboConfig(
        base_model=item["base_model"],
        residual_model=item["residual_model"],
        residual_scale=float(item["residual_scale"]),
        alpha=float(item.get("alpha", 1.0)),
        pca_components=int(item.get("pca_components", 16)),
        hidden_layer_sizes=tuple(int(value) for value in item.get("hidden_layer_sizes", [64])),
        max_iter=int(item.get("max_iter", 250)),
        random_state=int(item.get("random_state", 0)),
    )


def _candidate_record(item: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "base_model",
        "residual_model",
        "residual_scale",
        "alpha",
        "pca_components",
        "random_state",
    ]
    return {key: item.get(key) for key in keys}


def _metric_subset(row: pd.Series | dict[str, Any]) -> dict[str, Any]:
    return {
        "split": row["split"],
        "mae_delta": float(row["mae_delta"]),
        "mse_delta": float(row["mse_delta"]),
        "pearson_delta": float(row["pearson_delta"]),
        "spearman_logfc": float(row["spearman_logfc"]),
    }


def _lookup_metric(frame: pd.DataFrame, label: str) -> pd.Series:
    return frame.loc[frame["label"] == label].iloc[0]


def _per_class_summary(frame: pd.DataFrame) -> pd.DataFrame:
    metric_columns = ["mae_delta", "mse_delta", "pearson_delta", "spearman_logfc"]
    return (
        frame.groupby(["split", "candidate_id", "group_column", "group_value"], dropna=False)[
            metric_columns
        ]
        .mean(numeric_only=True)
        .reset_index()
    )


def _de_summary(frame: pd.DataFrame) -> pd.DataFrame:
    metric_columns = [
        column
        for column in frame.columns
        if column.startswith("top_") or column == "spearman_gene_rank"
    ]
    return (
        frame.groupby(["split", "candidate_id", "perturbation_type", "split_class"], dropna=False)[
            metric_columns
        ]
        .mean(numeric_only=True)
        .reset_index()
    )


def _write_report(
    run_dir: Path,
    *,
    config: dict[str, Any],
    validation_sweep: pd.DataFrame,
    selected_row: pd.Series,
    final_metrics: dict[str, Any],
    comparison: pd.DataFrame,
    per_class_summary: pd.DataFrame,
    de_summary: pd.DataFrame,
    split_audit: dict[str, Any],
    data_report_dir: Path,
    preparation: dict[str, Any],
) -> None:
    lines = [
        "# v0.16 Official GEARS Or Model Improvement Sprint",
        "",
        "## One-Line Result",
        "",
        _one_line_result(comparison, final_metrics),
        "",
        "## Dataset And Checksum",
        "",
        f"- Source: {config['benchmark']['source']}",
        f"- Local path: `{preparation['path']}`",
        f"- Checksum status: `{preparation['checksum_status']}`",
        "",
        "## Split Status",
        "",
        f"- Split: {config['benchmark']['split_definition']}",
        f"- Leakage audit passed: `{split_audit['overall_pass']}`",
        f"- Schema report: `{data_report_dir / 'schema_report.md'}`",
        "",
        "## Official GEARS Status",
        "",
        f"- Status: `{config['official_gears']['status']}`",
        f"- Dry-run output: `{config['official_gears']['dry_run_output']}`",
        "",
        "## Validation Selection",
        "",
        f"- Selection metric: `{config['selection']['metric']}` on validation split",
        f"- Selected candidate: `{selected_row['candidate_id']}`",
        "",
        _markdown_table(validation_sweep),
        "",
        "## Final Test Metrics",
        "",
        _markdown_table(pd.DataFrame([final_metrics])),
        "",
        "## Comparison To v0.14/v0.15",
        "",
        _markdown_table(comparison),
        "",
        "## seen0/seen1/seen2 Breakdown",
        "",
        _markdown_table(per_class_summary),
        "",
        "## DE20/DE50 Recovery",
        "",
        _markdown_table(de_summary),
        "",
        "## Claim Boundary",
        "",
        config["reporting"]["claim_boundary"],
        "",
    ]
    (run_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")


def _one_line_result(comparison: pd.DataFrame, final_metrics: dict[str, Any]) -> str:
    selected_label = f"v0.16_selected_{final_metrics['candidate_id']}"
    selected = comparison.loc[comparison["label"] == selected_label].iloc[0]
    improved = [
        key
        for key in (
            "beats_v014_weighted_mae",
            "beats_v014_weighted_mse",
            "beats_v014_single_pearson",
            "beats_v014_single_spearman",
        )
        if bool(selected[key])
    ]
    if improved:
        return f"v0.16 selected `{final_metrics['candidate_id']}` improved: {', '.join(improved)}."
    return (
        f"v0.16 selected `{final_metrics['candidate_id']}` by validation, but it did not "
        "beat the v0.14 global reference metrics on test."
    )


def _write_leakage_markdown(path: Path, audit: dict[str, Any]) -> None:
    lines = [
        "# v0.16 Leakage Audit",
        "",
        f"- Overall pass: `{audit['overall_pass']}`",
        f"- Leaked test combos: `{audit['leaked_test_combos']}`",
        "- Test deltas were not used for residual fitting or validation selection.",
        "",
        "```json",
        json.dumps(audit, indent=2, ensure_ascii=False),
        "```",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


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
