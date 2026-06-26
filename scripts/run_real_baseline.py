"""Run the v0.3 real-data baseline benchmark."""

from __future__ import annotations

import argparse
import json
import subprocess
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from evoprior_aivc.baselines import (
    AdditiveBaseline,
    MeanDeltaBaseline,
    NoChangeBaseline,
    RidgeBaseline,
    build_delta_dataset,
)
from evoprior_aivc.data.adapters import write_schema_report
from evoprior_aivc.data.download import prepare_dataset
from evoprior_aivc.data.preprocess import preprocess_adata
from evoprior_aivc.data.pseudobulk import aggregate_pseudobulk
from evoprior_aivc.data.real_loader import load_real_dataset
from evoprior_aivc.data.registry import DatasetRecord
from evoprior_aivc.data.splits import assign_group_holdout_split, assign_random_group_split
from evoprior_aivc.evaluation.evaluator import (
    evaluate_by_group,
    evaluate_delta_predictions,
    prediction_long_frame,
    subset_delta_dataset,
)
from evoprior_aivc.evaluation.leakage_checks import (
    assert_holdout_split_has_no_train_leakage,
    assert_no_target_derived_features,
    assert_required_split_labels,
)
from evoprior_aivc.evaluation.reports import write_real_baseline_report


def main() -> None:
    args = _parse_args()
    config = _load_yaml(Path(args.config))
    run_dir = _make_run_dir(config)
    git_commit = _git_commit()
    _write_yaml(run_dir / "resolved_config.yaml", config)
    _write_text_log(run_dir / "log.txt", ["started real baseline run"])

    preparation = prepare_dataset(config["data"], dry_run=False)
    dataset_record = DatasetRecord.from_config(config["data"])
    adata, schema_report = load_real_dataset(config["data"])
    write_schema_report(schema_report, run_dir)
    data_report_dir = Path("outputs/data_reports") / dataset_record.dataset_id / run_dir.name
    write_schema_report(schema_report, data_report_dir)
    adata = preprocess_adata(adata, config)
    expression, metadata = aggregate_pseudobulk(
        adata,
        groupby=tuple(config["pseudobulk"]["groupby"]),
        layer=config["pseudobulk"].get("layer"),
        min_cells=int(config["pseudobulk"]["min_cells"]),
        aggregation=config["pseudobulk"]["aggregation"],
    )
    delta_dataset = build_delta_dataset(
        expression,
        metadata,
        control_label=config["delta"]["control_label"],
        match_columns=tuple(config["delta"]["match_columns"]),
        fallback=config["delta"].get("control_fallback", "raise"),
    )

    assert_no_target_derived_features(config["features"]["allowed_feature_columns"])

    metrics_rows: list[dict[str, Any]] = []
    breakdown_frames: list[pd.DataFrame] = []
    prediction_frames: list[pd.DataFrame] = []
    split_frames: list[pd.DataFrame] = []
    failure_frames: list[pd.DataFrame] = []

    for split_mode, split_config in config["splits"].items():
        split = _make_split(split_mode, split_config, delta_dataset.metadata)
        assert_required_split_labels(split)
        if "holdout" in split_config:
            assert_holdout_split_has_no_train_leakage(
                delta_dataset.metadata,
                split,
                holdout=split_config["holdout"],
            )
        split_frames.append(_split_frame(split_mode, split, delta_dataset.metadata))
        train = subset_delta_dataset(delta_dataset, split == "train")

        for baseline in _baseline_instances(config["baselines"]):
            baseline.fit(train)
            for split_label in ("val", "test"):
                mask = split == split_label
                if not mask.any():
                    continue
                query = subset_delta_dataset(delta_dataset, mask)
                predicted_delta = baseline.predict_delta(query)
                metrics = evaluate_delta_predictions(query, predicted_delta)
                metrics_rows.append(
                    {
                        "experiment_id": config["experiment_id"],
                        "dataset_id": dataset_record.dataset_id,
                        "split_mode": split_mode,
                        "split": split_label,
                        "baseline": baseline.name,
                        "n_examples": len(query.group_ids),
                        **metrics,
                    }
                )
                breakdown = evaluate_by_group(
                    query,
                    predicted_delta,
                    group_columns=("cell_type", "perturbation"),
                )
                if not breakdown.empty:
                    breakdown.insert(0, "baseline", baseline.name)
                    breakdown.insert(0, "split", split_label)
                    breakdown.insert(0, "split_mode", split_mode)
                    breakdown_frames.append(breakdown)
                prediction_frames.append(
                    prediction_long_frame(
                        query,
                        predicted_delta,
                        baseline=baseline.name,
                        split_mode=split_mode,
                        split_label=split_label,
                    )
                )
                failure_frames.append(
                    _failure_cases(
                        query,
                        predicted_delta,
                        baseline=baseline.name,
                        split_mode=split_mode,
                        split_label=split_label,
                    )
                )

    metrics_df = pd.DataFrame(metrics_rows)
    breakdown_df = _concat_frames(breakdown_frames)
    predictions_df = pd.concat(prediction_frames, ignore_index=True)
    split_df = pd.concat(split_frames, ignore_index=True)
    failures_df = _concat_frames(failure_frames).sort_values("mae_delta", ascending=False)
    top_failures = failures_df.head(int(config["reporting"]["top_failure_cases"]))
    split_summary = _split_summary(split_df, delta_dataset.metadata)
    group_summary = _group_summary(adata, expression, metadata, delta_dataset)

    metrics_df.to_json(run_dir / "metrics.json", orient="records", indent=2)
    metrics_df.to_csv(run_dir / "metrics.csv", index=False)
    breakdown_df.to_csv(run_dir / "breakdown.csv", index=False)
    predictions_df.to_csv(run_dir / "predictions.csv", index=False)
    split_df.to_csv(run_dir / "split_manifest.csv", index=False)
    failures_df.to_csv(run_dir / "failure_cases.csv", index=False)
    (run_dir / "dataset_registry.json").write_text(
        json.dumps(dataset_record.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (run_dir / "dataset_preparation.json").write_text(
        json.dumps(preparation.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (run_dir / "schema_report.json").write_text(
        json.dumps(schema_report.__dict__, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (run_dir / "group_summary.json").write_text(
        json.dumps(group_summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    write_real_baseline_report(
        report_path=run_dir / "report.md",
        experiment_id=config["experiment_id"],
        dataset_id=dataset_record.dataset_id,
        output_dir=run_dir,
        git_commit=git_commit,
        metrics=metrics_df,
        breakdown=breakdown_df,
        split_summary=split_summary,
        group_summary=group_summary,
        top_failures=top_failures,
        assumptions=config["reporting"]["assumptions"],
        limitations=config["reporting"]["limitations"],
    )
    _write_text_log(
        run_dir / "log.txt",
        [
            "completed real baseline run",
            f"metrics rows: {metrics_df.shape[0]}",
            f"predictions rows: {predictions_df.shape[0]}",
        ],
        append=True,
    )
    print(run_dir)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to real baseline YAML config.")
    return parser.parse_args()


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _write_yaml(path: Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=False, allow_unicode=True)


def _make_run_dir(config: dict[str, Any]) -> Path:
    dataset_id = config["data"]["dataset"]["dataset_id"]
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    root = Path(config["output_root"]) / config["output_prefix"] / dataset_id / timestamp
    root.mkdir(parents=True, exist_ok=False)
    return root


def _make_split(split_mode: str, split_config: dict[str, Any], metadata: pd.DataFrame) -> pd.Series:
    if split_mode == "random_group":
        return assign_random_group_split(
            metadata,
            val_fraction=float(split_config["val_fraction"]),
            test_fraction=float(split_config["test_fraction"]),
            seed=int(split_config["seed"]),
        )
    if split_mode.startswith("heldout_"):
        return assign_group_holdout_split(
            metadata,
            split_config["holdout"],
            val_fraction=float(split_config["val_fraction"]),
            seed=int(split_config["seed"]),
        )
    raise ValueError(f"unsupported split mode: {split_mode}")


def _baseline_instances(configs: list[dict[str, Any]]):
    for config in configs:
        name = config["name"]
        if name == "no_change":
            yield NoChangeBaseline()
        elif name == "mean_delta":
            yield MeanDeltaBaseline(fallback=config.get("fallback", "global"))
        elif name == "additive":
            yield AdditiveBaseline()
        elif name == "ridge":
            yield RidgeBaseline(alpha=float(config.get("alpha", 1.0)))
        else:
            raise ValueError(f"unsupported baseline: {name}")


def _split_frame(split_mode: str, split: pd.Series, metadata: pd.DataFrame) -> pd.DataFrame:
    frame = metadata.copy()
    frame.insert(0, "split", split.astype(str).to_numpy())
    frame.insert(0, "split_mode", split_mode)
    frame.insert(0, "group_id", metadata.index)
    return frame.reset_index(drop=True)


def _failure_cases(
    query,
    predicted_delta: pd.DataFrame,
    *,
    baseline: str,
    split_mode: str,
    split_label: str,
):
    observed = query.observed_delta
    absolute_error = (observed - predicted_delta.loc[observed.index, observed.columns]).abs()
    rows = []
    for group_id, values in absolute_error.iterrows():
        row = {
            "split_mode": split_mode,
            "split": split_label,
            "baseline": baseline,
            "group_id": group_id,
            "mae_delta": float(values.mean()),
            "max_abs_delta_error": float(values.max()),
        }
        for column in ("cell_type", "perturbation", "guide_id", "n_cells"):
            if column in query.metadata.columns:
                row[column] = query.metadata.loc[group_id, column]
        rows.append(row)
    return pd.DataFrame(rows)


def _split_summary(split_df: pd.DataFrame, metadata: pd.DataFrame) -> pd.DataFrame:
    summary = (
        split_df.groupby(["split_mode", "split"], dropna=False)
        .agg(n_groups=("group_id", "count"), n_cells=("n_cells", "sum"))
        .reset_index()
    )
    return summary


def _group_summary(
    adata,
    expression: pd.DataFrame,
    metadata: pd.DataFrame,
    delta_dataset,
) -> dict[str, object]:
    return {
        "n_cells_after_preprocessing": int(adata.n_obs),
        "n_genes_after_preprocessing": int(adata.n_vars),
        "n_pseudobulk_groups": int(expression.shape[0]),
        "n_delta_examples": int(len(delta_dataset.group_ids)),
        "min_group_cells": int(metadata["n_cells"].min()),
        "max_group_cells": int(metadata["n_cells"].max()),
        "median_group_cells": float(metadata["n_cells"].median()),
        "perturbations": int(metadata["perturbation"].nunique()),
        "cell_types": (
            int(metadata["cell_type"].nunique()) if "cell_type" in metadata.columns else 0
        ),
    }


def _concat_frames(frames: list[pd.DataFrame]) -> pd.DataFrame:
    nonempty = [frame for frame in frames if not frame.empty]
    if not nonempty:
        return pd.DataFrame()
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="The behavior of DataFrame concatenation with empty or all-NA entries",
            category=FutureWarning,
        )
        return pd.concat(nonempty, ignore_index=True)


def _git_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def _write_text_log(path: Path, lines: list[str], *, append: bool = False) -> None:
    mode = "a" if append else "w"
    with path.open(mode, encoding="utf-8") as handle:
        for line in lines:
            handle.write(f"{datetime.now(timezone.utc).isoformat()} {line}\n")


if __name__ == "__main__":
    main()
