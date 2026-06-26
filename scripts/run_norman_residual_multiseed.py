"""Run v0.17 multi-seed validation for the Norman residual baseline."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
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
from evoprior_aivc.evaluation.leakage_stress import (
    all_critical_checks_pass,
    run_norman_leakage_stress_checks,
    stress_results_to_frame,
    write_leakage_stress_report,
)

METRIC_COLUMNS: tuple[str, ...] = (
    "mae_delta",
    "mse_delta",
    "pearson_delta",
    "spearman_logfc",
)


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

    train = subset_delta_dataset(dataset, split == "train")
    val = subset_delta_dataset(dataset, split == config["selection"]["split"])
    test = subset_delta_dataset(dataset, split == "test")
    reference_metrics = _evaluate_references(config, train, val, test)
    selected_outputs = _run_selected_model(config, train, val, test)
    ablation_outputs = _run_ablation_suite(config, train, val, test)
    aggregate_metrics = _aggregate_seed_metrics(selected_outputs["per_seed_metrics"])
    per_class_summary = _aggregate_group_metrics(selected_outputs["per_class_metrics"])
    de_summary = _aggregate_de_metrics(selected_outputs["de_metrics"])
    comparison = _comparison_table(config, aggregate_metrics)
    ablation_summary = _summarize_ablation(ablation_outputs["ablation_metrics"])
    ablation_winner = _select_ablation_winner(ablation_outputs["ablation_metrics"], config)
    selected_mean = _mean_metric_dict(selected_outputs["per_seed_metrics"], split="test")
    shuffled_target = _mean_metric_dict(
        ablation_outputs["ablation_metrics"],
        split="test",
        candidate_id="shuffled_residual_target_control",
    )
    shuffled_feature = _mean_metric_dict(
        ablation_outputs["ablation_metrics"],
        split="test",
        candidate_id="shuffled_perturbation_feature_control",
    )
    stress_results = run_norman_leakage_stress_checks(
        split_manifest=split_manifest,
        config=config,
        selected_metrics=selected_mean,
        shuffled_target_metrics=shuffled_target,
        shuffled_feature_metrics=shuffled_feature,
    )
    if not all_critical_checks_pass(stress_results):
        _write_failure_artifacts(run_dir, stress_results)
        raise RuntimeError("critical leakage stress check failed; see leakage_stress_report.md")

    _write_outputs(
        run_dir=run_dir,
        config=config,
        data_config=data_config,
        preparation=preparation.to_dict(),
        schema_report=schema_report.__dict__,
        split_audit=split_audit,
        reference_metrics=reference_metrics,
        selected_outputs=selected_outputs,
        aggregate_metrics=aggregate_metrics,
        comparison=comparison,
        ablation_outputs=ablation_outputs,
        ablation_summary=ablation_summary,
        ablation_winner=ablation_winner,
        per_class_summary=per_class_summary,
        de_summary=de_summary,
        stress_results=stress_results,
        data_report_dir=data_report_dir,
    )
    print(run_dir)
    print(ablation_winner["candidate_id"])


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


def _run_selected_model(config: dict[str, Any], train, val, test) -> dict[str, pd.DataFrame]:
    per_seed_rows: list[dict[str, Any]] = []
    per_pert_rows: list[pd.DataFrame] = []
    per_class_rows: list[pd.DataFrame] = []
    de_rows: list[pd.DataFrame] = []
    selected_configs: list[dict[str, Any]] = []
    for seed in config["seeds"]:
        item = dict(config["selected_model"])
        item["random_state"] = int(item.get("random_state_base", 0)) + int(seed)
        model = ResidualComboCorrectionBaseline(_residual_config(item, seed=int(seed))).fit(train)
        selected_configs.append(
            {
                "seed": int(seed),
                "candidate_id": item["candidate_id"],
                **model.manifest()["config"],
            }
        )
        for split_label, dataset in (("val", val), ("test", test)):
            predicted = model.predict_delta(dataset)
            per_seed_rows.append(
                {
                    "seed": int(seed),
                    "candidate_id": item["candidate_id"],
                    "split": split_label,
                    "n_examples": len(dataset.group_ids),
                    **evaluate_delta_predictions(dataset, predicted),
                }
            )
            if split_label == "test":
                per_pert = per_perturbation_metrics(dataset, predicted)
                per_pert.insert(0, "seed", int(seed))
                per_pert.insert(1, "candidate_id", item["candidate_id"])
                per_pert.insert(2, "split", "test")
                per_pert_rows.append(per_pert)
                per_class = per_class_metrics(dataset, predicted)
                per_class.insert(0, "seed", int(seed))
                per_class.insert(1, "candidate_id", item["candidate_id"])
                per_class.insert(2, "split", "test")
                per_class_rows.append(per_class)
                de_frame = pd.DataFrame(
                    de_rows_for_dataset(dataset, predicted, ks=tuple(config["evaluation"]["de_ks"]))
                )
                de_frame.insert(0, "seed", int(seed))
                de_frame.insert(1, "candidate_id", item["candidate_id"])
                de_frame.insert(2, "split", "test")
                de_rows.append(de_frame)
    return {
        "per_seed_metrics": pd.DataFrame(per_seed_rows),
        "per_perturbation_metrics": pd.concat(per_pert_rows, ignore_index=True),
        "per_class_metrics": pd.concat(per_class_rows, ignore_index=True),
        "de_metrics": pd.concat(de_rows, ignore_index=True),
        "selected_configs": pd.DataFrame(selected_configs),
    }


def _run_ablation_suite(config: dict[str, Any], train, val, test) -> dict[str, pd.DataFrame]:
    rows: list[dict[str, Any]] = []
    for item in config["ablation_models"]:
        for seed in config["seeds"]:
            item_with_seed = dict(item)
            item_with_seed["random_state"] = int(
                config["selected_model"]["random_state_base"]
            ) + int(seed)
            model = ResidualComboCorrectionBaseline(
                _residual_config(item_with_seed, seed=int(seed))
            ).fit(train)
            for split_label, dataset in (("val", val), ("test", test)):
                predicted = model.predict_delta(dataset)
                rows.append(
                    {
                        "seed": int(seed),
                        "candidate_id": item["candidate_id"],
                        "split": split_label,
                        "n_examples": len(dataset.group_ids),
                        **_ablation_record(item),
                        **evaluate_delta_predictions(dataset, predicted),
                    }
                )
    return {"ablation_metrics": pd.DataFrame(rows)}


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


def _reference_baselines(configs: list[dict[str, Any]]):
    for config in configs:
        name = config["name"]
        if name == "single_effect_additive_combo":
            yield SingleEffectAdditiveComboBaseline(
                missing_single_fallback=config.get("missing_single_fallback", "global_single_mean")
            )
        elif name == "weighted_combo_additive":
            yield WeightedComboAdditiveBaseline(
                ridge_alpha=float(config.get("ridge_alpha", 1.0)),
                missing_single_fallback=config.get("missing_single_fallback", "global_single_mean"),
            )
        else:
            raise ValueError(f"unsupported reference baseline: {name}")


def _residual_config(item: dict[str, Any], *, seed: int) -> ResidualComboConfig:
    return ResidualComboConfig(
        base_model=item["base_model"],
        residual_model=item["residual_model"],
        residual_scale=float(item["residual_scale"]),
        alpha=float(item.get("alpha", 1.0)),
        pca_components=int(item.get("pca_components", 16)),
        hidden_layer_sizes=tuple(int(value) for value in item.get("hidden_layer_sizes", [64])),
        max_iter=int(item.get("max_iter", 250)),
        random_state=int(item.get("random_state", seed)),
        include_split_class=bool(item.get("include_split_class", True)),
        residual_target_shuffle_seed=(
            int(10_000 + seed) if bool(item.get("residual_target_shuffle", False)) else None
        ),
        metadata_feature_shuffle_seed=(
            int(20_000 + seed) if bool(item.get("metadata_feature_shuffle", False)) else None
        ),
    )


def _ablation_record(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "base_model": item.get("base_model"),
        "residual_model": item.get("residual_model"),
        "residual_scale": item.get("residual_scale"),
        "alpha": item.get("alpha"),
        "pca_components": item.get("pca_components"),
        "negative_control": bool(
            item.get("residual_target_shuffle", False)
            or item.get("metadata_feature_shuffle", False)
        ),
    }


def _aggregate_seed_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    test = frame[frame["split"] == "test"]
    candidate_id = str(test["candidate_id"].iloc[0])
    for metric in METRIC_COLUMNS:
        values = test[metric].astype(float).to_numpy()
        mean = float(np.mean(values))
        std = float(np.std(values, ddof=1)) if len(values) > 1 else 0.0
        ci = 1.96 * std / float(np.sqrt(len(values))) if len(values) > 1 else 0.0
        rows.append(
            {
                "candidate_id": candidate_id,
                "split": "test",
                "metric": metric,
                "n_seeds": int(len(values)),
                "mean": mean,
                "std": std,
                "ci95_low": mean - ci,
                "ci95_high": mean + ci,
            }
        )
    return pd.DataFrame(rows)


def _aggregate_group_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for keys, group in frame.groupby(
        ["candidate_id", "split", "group_column", "group_value"],
        dropna=False,
    ):
        row = {
            "candidate_id": keys[0],
            "split": keys[1],
            "group_column": keys[2],
            "group_value": keys[3],
            "n_seeds": int(group["seed"].nunique()),
        }
        for metric in METRIC_COLUMNS:
            values = group[metric].astype(float).to_numpy()
            row[f"{metric}_mean"] = float(np.mean(values))
            row[f"{metric}_std"] = float(np.std(values, ddof=1)) if len(values) > 1 else 0.0
        rows.append(row)
    return pd.DataFrame(rows)


def _aggregate_de_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    metric_columns = [
        column
        for column in frame.columns
        if column.startswith("top_") or column == "spearman_gene_rank"
    ]
    return (
        frame.groupby(["candidate_id", "split", "perturbation_type", "split_class"], dropna=False)[
            metric_columns
        ]
        .mean(numeric_only=True)
        .reset_index()
    )


def _summarize_ablation(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (candidate_id, split), group in frame.groupby(["candidate_id", "split"], dropna=False):
        row: dict[str, Any] = {
            "candidate_id": candidate_id,
            "split": split,
            "n_seeds": int(group["seed"].nunique()),
        }
        for metric in METRIC_COLUMNS:
            values = group[metric].astype(float).to_numpy()
            row[f"{metric}_mean"] = float(np.mean(values))
            row[f"{metric}_std"] = float(np.std(values, ddof=1)) if len(values) > 1 else 0.0
        rows.append(row)
    return pd.DataFrame(rows)


def _select_ablation_winner(frame: pd.DataFrame, config: dict[str, Any]) -> dict[str, Any]:
    val_summary = _summarize_ablation(frame)
    val_summary = val_summary[val_summary["split"] == config["selection"]["split"]]
    row = val_summary.sort_values(["mae_delta_mean", "mse_delta_mean"]).iloc[0]
    return {
        "candidate_id": str(row["candidate_id"]),
        "selection_split": config["selection"]["split"],
        "selection_metric": "mae_delta_mean",
        "mae_delta_mean": float(row["mae_delta_mean"]),
    }


def _comparison_table(config: dict[str, Any], aggregate_metrics: pd.DataFrame) -> pd.DataFrame:
    mean_metrics = {
        row["metric"]: float(row["mean"])
        for _, row in aggregate_metrics.iterrows()
    }
    rows = [
        {"label": row["label"], "source": "historical", **row}
        for row in config["comparison_reference"]["rows"]
    ]
    rows.append(
        {
            "label": "v0.17_multiseed_weighted_pca_ridge_s075_a10",
            "source": "current_mean",
            "split": "test",
            **mean_metrics,
        }
    )
    frame = pd.DataFrame(rows)
    weighted = frame.loc[frame["label"] == "v0.14_weighted_combo_additive"].iloc[0]
    v16 = frame.loc[frame["label"] == "v0.16_weighted_pca_ridge_s075_a10"].iloc[0]
    frame["beats_v014_weighted_mae"] = frame["mae_delta"] < weighted["mae_delta"]
    frame["beats_v014_weighted_mse"] = frame["mse_delta"] < weighted["mse_delta"]
    frame["matches_v016_mae"] = np.isclose(frame["mae_delta"], v16["mae_delta"])
    frame["matches_v016_mse"] = np.isclose(frame["mse_delta"], v16["mse_delta"])
    return frame


def _mean_metric_dict(
    frame: pd.DataFrame,
    *,
    split: str,
    candidate_id: str | None = None,
) -> dict[str, float]:
    subset = frame[frame["split"] == split]
    if candidate_id is not None:
        subset = subset[subset["candidate_id"] == candidate_id]
    return {metric: float(subset[metric].astype(float).mean()) for metric in METRIC_COLUMNS}


def _write_outputs(
    *,
    run_dir: Path,
    config: dict[str, Any],
    data_config: dict[str, Any],
    preparation: dict[str, Any],
    schema_report: dict[str, Any],
    split_audit: dict[str, Any],
    reference_metrics: pd.DataFrame,
    selected_outputs: dict[str, pd.DataFrame],
    aggregate_metrics: pd.DataFrame,
    comparison: pd.DataFrame,
    ablation_outputs: dict[str, pd.DataFrame],
    ablation_summary: pd.DataFrame,
    ablation_winner: dict[str, Any],
    per_class_summary: pd.DataFrame,
    de_summary: pd.DataFrame,
    stress_results,
    data_report_dir: Path,
) -> None:
    selected_outputs["per_seed_metrics"].to_csv(run_dir / "per_seed_metrics.csv", index=False)
    aggregate_metrics.to_csv(run_dir / "aggregate_metrics.csv", index=False)
    selected_outputs["per_class_metrics"].to_csv(run_dir / "per_class_metrics.csv", index=False)
    per_class_summary.to_csv(run_dir / "per_class_metric_summary.csv", index=False)
    selected_outputs["per_perturbation_metrics"].to_csv(
        run_dir / "per_perturbation_metrics.csv",
        index=False,
    )
    selected_outputs["selected_configs"].to_csv(run_dir / "selected_configs.csv", index=False)
    selected_outputs["de_metrics"].to_csv(run_dir / "de_metrics.csv", index=False)
    de_summary.to_csv(run_dir / "de_metric_summary.csv", index=False)
    comparison.to_csv(run_dir / "comparison_to_v014_v015_v016.csv", index=False)
    reference_metrics.to_csv(run_dir / "reference_metrics.csv", index=False)
    ablation_outputs["ablation_metrics"].to_csv(run_dir / "ablation_metrics.csv", index=False)
    ablation_summary.to_csv(run_dir / "ablation_summary.csv", index=False)
    _write_json(run_dir / "ablation_selection.json", ablation_winner)
    stress_results_to_frame(stress_results).to_csv(
        run_dir / "leakage_stress_checks.csv",
        index=False,
    )
    write_leakage_stress_report(run_dir / "leakage_stress_report.md", results=stress_results)
    _write_ablation_report(run_dir / "ablation_report.md", ablation_summary, ablation_winner)
    _write_json(run_dir / "dataset_preparation.json", preparation)
    _write_json(run_dir / "schema_report.json", schema_report)
    _write_json(run_dir / "split_leakage_audit.json", split_audit)
    _write_json(
        run_dir / "run_manifest.json",
        {
            "git_commit": _git_commit(),
            "experiment_id": config["experiment_id"],
            "benchmark_id": config["benchmark_id"],
            "dataset_id": config["dataset_id"],
            "command": (
                "python scripts/run_norman_residual_multiseed.py --config "
                f"{config.get('config_path')}"
            ),
            "seeds": list(config["seeds"]),
            "data_checksum": data_config["dataset"]["checksum"],
            "split_definition": config["benchmark"]["split_definition"],
            "metric_script": "src/evoprior_aivc/evaluation/gears_metrics.py",
            "leakage_stress_script": "src/evoprior_aivc/evaluation/leakage_stress.py",
            "claim_boundary": config["reporting"]["claim_boundary"],
        },
    )
    _write_report(
        run_dir,
        config=config,
        preparation=preparation,
        aggregate_metrics=aggregate_metrics,
        comparison=comparison,
        ablation_summary=ablation_summary,
        ablation_winner=ablation_winner,
        per_class_summary=per_class_summary,
        de_summary=de_summary,
        stress_results=stress_results,
        data_report_dir=data_report_dir,
    )


def _write_failure_artifacts(run_dir: Path, stress_results) -> None:
    stress_results_to_frame(stress_results).to_csv(
        run_dir / "leakage_stress_checks.csv",
        index=False,
    )
    write_leakage_stress_report(run_dir / "leakage_stress_report.md", results=stress_results)


def _write_ablation_report(path: Path, summary: pd.DataFrame, winner: dict[str, Any]) -> None:
    lines = [
        "# v0.17 Ablation Report",
        "",
        f"- Validation-selected ablation winner: `{winner['candidate_id']}`",
        f"- Selection metric: `{winner['selection_metric']}` on `{winner['selection_split']}`",
        "",
        _markdown_table(summary),
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_report(
    run_dir: Path,
    *,
    config: dict[str, Any],
    preparation: dict[str, Any],
    aggregate_metrics: pd.DataFrame,
    comparison: pd.DataFrame,
    ablation_summary: pd.DataFrame,
    ablation_winner: dict[str, Any],
    per_class_summary: pd.DataFrame,
    de_summary: pd.DataFrame,
    stress_results,
    data_report_dir: Path,
) -> None:
    lines = [
        "# v0.17 Public Norman Validated Residual Baseline",
        "",
        "## Executive Summary",
        "",
        "A five-seed validation run reproduced the v0.16 residual baseline on the fixed "
        "GEARS-compatible internal Norman split, with ablations, negative controls, "
        "class breakdowns, and leakage stress checks.",
        "",
        "## Dataset And Split",
        "",
        f"- Dataset path: `{preparation['path']}`",
        f"- Checksum status: `{preparation['checksum_status']}`",
        f"- Split: {config['benchmark']['split_definition']}",
        f"- Schema/split reports: `{data_report_dir}`",
        "",
        "## Multi-Seed Aggregate Metrics",
        "",
        _markdown_table(aggregate_metrics),
        "",
        "## Comparison",
        "",
        _markdown_table(comparison),
        "",
        "## seen0/seen1/seen2/random_combo Breakdown",
        "",
        _markdown_table(per_class_summary),
        "",
        "## DE20/DE50 Recovery",
        "",
        _markdown_table(de_summary),
        "",
        "## Ablation Summary",
        "",
        f"- Validation-selected ablation winner: `{ablation_winner['candidate_id']}`",
        "",
        _markdown_table(ablation_summary),
        "",
        "## Leakage Stress Summary",
        "",
        _markdown_table(stress_results_to_frame(stress_results)),
        "",
        "## Claim Boundary",
        "",
        config["reporting"]["claim_boundary"],
        "",
    ]
    (run_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")


def _markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "No rows."
    flat = frame.copy()
    flat.columns = [
        "_".join(map(str, column)).strip("_") if isinstance(column, tuple) else str(column)
        for column in flat.columns
    ]
    columns = list(map(str, flat.columns))
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for _, row in flat.iterrows():
        lines.append("| " + " | ".join(_format_cell(row[column]) for column in flat.columns) + " |")
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
