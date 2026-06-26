"""Run the synthetic v0.2 baseline smoke experiment."""

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
from evoprior_aivc.data.pseudobulk import aggregate_pseudobulk
from evoprior_aivc.data.splits import assign_group_holdout_split, assign_random_group_split
from evoprior_aivc.data.synthetic import make_synthetic_perturbation_adata
from evoprior_aivc.data.validate import validate_adata_schema
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
from evoprior_aivc.evaluation.reports import write_baseline_report


def main() -> None:
    args = _parse_args()
    config_path = Path(args.config)
    config = _load_yaml(config_path)
    run_dir = _make_run_dir(config)
    git_commit = _git_commit()

    _write_yaml(run_dir / "resolved_config.yaml", config)
    _write_text_log(run_dir / "log.txt", ["started synthetic baseline smoke run"])

    adata = make_synthetic_perturbation_adata(seed=config["seed"], **config["synthetic"])
    schema_report = validate_adata_schema(adata)
    expression, metadata = aggregate_pseudobulk(
        adata,
        groupby=tuple(config["pseudobulk"]["groupby"]),
        min_cells=int(config["pseudobulk"]["min_cells"]),
        aggregation=config["pseudobulk"]["aggregation"],
    )
    delta_dataset = build_delta_dataset(
        expression,
        metadata,
        control_label=config["delta"]["control_label"],
        match_columns=tuple(config["delta"]["match_columns"]),
    )

    assert_no_target_derived_features(
        ["control_expression", "perturbation", "cell_type", "donor"]
    )

    metrics_rows: list[dict[str, Any]] = []
    breakdown_frames: list[pd.DataFrame] = []
    prediction_frames: list[pd.DataFrame] = []
    split_frames: list[pd.DataFrame] = []

    for split_mode, split_config in config["splits"].items():
        split = _make_split(split_mode, split_config, delta_dataset.metadata)
        assert_required_split_labels(split)
        if "holdout" in split_config:
            assert_holdout_split_has_no_train_leakage(
                delta_dataset.metadata,
                split,
                holdout=split_config["holdout"],
            )
        split_frames.append(
            pd.DataFrame(
                {
                    "split_mode": split_mode,
                    "group_id": delta_dataset.metadata.index,
                    "split": split.astype(str).to_numpy(),
                }
            )
        )

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

    metrics_df = pd.DataFrame(metrics_rows)
    nonempty_breakdowns = [frame for frame in breakdown_frames if not frame.empty]
    if nonempty_breakdowns:
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message="The behavior of DataFrame concatenation with empty or all-NA entries",
                category=FutureWarning,
            )
            breakdown_df = pd.concat(nonempty_breakdowns, ignore_index=True)
    else:
        breakdown_df = pd.DataFrame()
    predictions_df = pd.concat(prediction_frames, ignore_index=True)
    split_df = pd.concat(split_frames, ignore_index=True)

    metrics_df.to_json(run_dir / "metrics.json", orient="records", indent=2)
    metrics_df.to_csv(run_dir / "metrics.csv", index=False)
    breakdown_df.to_csv(run_dir / "breakdown.csv", index=False)
    predictions_df.to_csv(run_dir / "predictions.csv", index=False)
    split_df.to_csv(run_dir / "split_assignments.csv", index=False)
    (run_dir / "schema_report.json").write_text(
        json.dumps(schema_report.__dict__, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    write_baseline_report(
        report_path=run_dir / "report.md",
        experiment_id=config["experiment_id"],
        output_dir=run_dir,
        git_commit=git_commit,
        metrics=metrics_df,
        breakdown=breakdown_df,
        assumptions=[
            "Synthetic data are deterministic for a fixed seed and are used only for engineering validation.",
            "Control expression matched by cell_type and donor is treated as an allowed model input.",
            "Ridge uses one-hot metadata with unknown categories ignored at prediction time.",
        ],
        limitations=[
            "No real public perturbation dataset is ingested in v0.2.",
            "Synthetic performance does not support biological claims.",
            "No EvoPrior neural model, lineage prior, or gene conservation prior is implemented.",
        ],
    )
    _write_text_log(
        run_dir / "log.txt",
        [
            "completed synthetic baseline smoke run",
            f"metrics rows: {metrics_df.shape[0]}",
            f"predictions rows: {predictions_df.shape[0]}",
        ],
        append=True,
    )
    print(run_dir)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to a YAML experiment config.")
    return parser.parse_args()


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _write_yaml(path: Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=False, allow_unicode=True)


def _make_run_dir(config: dict[str, Any]) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    root = Path(config["output_root"]) / config["output_prefix"] / timestamp
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
