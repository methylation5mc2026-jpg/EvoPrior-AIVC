"""Run v0.4 repeated real-data baseline evaluation."""

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
    RidgeBaseline,
    RidgeCVBaseline,
    build_delta_dataset,
)
from evoprior_aivc.data.download import prepare_dataset
from evoprior_aivc.data.preprocess import preprocess_adata
from evoprior_aivc.data.pseudobulk import aggregate_pseudobulk
from evoprior_aivc.data.real_loader import load_real_dataset
from evoprior_aivc.data.registry import DatasetRecord
from evoprior_aivc.data.splits import assign_group_holdout_split, assign_random_group_split
from evoprior_aivc.evaluation.de_metrics import de_recovery_metrics
from evoprior_aivc.evaluation.evaluator import evaluate_delta_predictions, subset_delta_dataset
from evoprior_aivc.evaluation.leakage_checks import (
    assert_holdout_split_has_no_train_leakage,
    assert_no_target_derived_features,
    assert_required_split_labels,
)
from evoprior_aivc.evaluation.perturbation_metrics import (
    candidate_profiles_from_observed,
    perturbation_retrieval_metrics,
    summarize_retrieval,
)
from evoprior_aivc.evaluation.repeated import perturbations_with_min_groups, repeated_seeds
from evoprior_aivc.evaluation.reports import write_v04_strengthening_report
from evoprior_aivc.evaluation.statistics import summarize_metric_table


def main() -> None:
    args = _parse_args()
    config = _load_yaml(Path(args.config))
    run_dir = _make_run_dir(config)
    run_dir.mkdir(parents=True, exist_ok=False)
    _write_yaml(run_dir / "resolved_config.yaml", config)
    git_commit = _git_commit()
    dataset_record = DatasetRecord.from_config(config["data"])

    preparation = prepare_dataset(config["data"], dry_run=False)
    adata, schema_report = load_real_dataset(config["data"])
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
        fallback=config["delta"].get("control_fallback", "raise"),
    )
    assert_no_target_derived_features(config["features"]["allowed_feature_columns"])

    metric_rows: list[dict[str, Any]] = []
    retrieval_rows: list[dict[str, Any]] = []
    de_rows: list[dict[str, Any]] = []
    skipped_frames: list[pd.DataFrame] = []

    repeated = config["evaluation"]["repeated_random_group"]
    if repeated.get("enabled", True):
        for repeat_id, seed in enumerate(
            repeated_seeds(int(repeated["seed_start"]), int(repeated["n_repeats"]))
        ):
            split = assign_random_group_split(
                dataset.metadata,
                val_fraction=float(repeated["val_fraction"]),
                test_fraction=float(repeated["test_fraction"]),
                seed=seed,
            )
            assert_required_split_labels(split)
            _evaluate_split(
                config,
                dataset,
                split,
                split_mode="repeated_random_group",
                repeat_id=repeat_id,
                seed=seed,
                metric_rows=metric_rows,
                retrieval_rows=retrieval_rows,
                de_rows=de_rows,
            )

    suite = config["evaluation"]["leave_one_perturbation_suite"]
    if suite.get("enabled", True):
        eligible, skipped = perturbations_with_min_groups(
            dataset.metadata,
            min_test_groups=int(suite["min_test_groups"]),
        )
        if not skipped.empty:
            skipped.insert(0, "split_mode", "leave_one_perturbation_suite")
            skipped_frames.append(skipped)
        for repeat_id, perturbation in enumerate(eligible):
            split = assign_group_holdout_split(
                dataset.metadata,
                holdout={"perturbation": [perturbation]},
                val_fraction=float(suite["val_fraction"]),
                seed=int(suite["seed"]) + repeat_id,
            )
            assert_required_split_labels(split)
            assert_holdout_split_has_no_train_leakage(
                dataset.metadata,
                split,
                holdout={"perturbation": [perturbation]},
            )
            _evaluate_split(
                config,
                dataset,
                split,
                split_mode="leave_one_perturbation_suite",
                repeat_id=repeat_id,
                seed=int(suite["seed"]) + repeat_id,
                heldout_perturbation=perturbation,
                metric_rows=metric_rows,
                retrieval_rows=retrieval_rows,
                de_rows=de_rows,
            )

    metrics = pd.DataFrame(metric_rows)
    retrieval = pd.DataFrame(retrieval_rows)
    de_metrics = pd.DataFrame(de_rows)
    skipped_perturbations = (
        pd.concat(skipped_frames, ignore_index=True) if skipped_frames else pd.DataFrame()
    )
    metric_summary = summarize_metric_table(
        metrics,
        group_columns=("split_mode", "split", "baseline"),
        metric_columns=tuple(config["evaluation"]["metric_columns"]),
    )
    retrieval_summary = _retrieval_summary_table(retrieval)
    de_summary = _de_summary_table(de_metrics)

    metrics.to_csv(run_dir / "per_run_metrics.csv", index=False)
    metric_summary.to_csv(run_dir / "metric_summary.csv", index=False)
    retrieval.to_csv(run_dir / "retrieval_rows.csv", index=False)
    retrieval_summary.to_csv(run_dir / "retrieval_summary.csv", index=False)
    de_metrics.to_csv(run_dir / "de_metrics.csv", index=False)
    de_summary.to_csv(run_dir / "de_summary.csv", index=False)
    skipped_perturbations.to_csv(run_dir / "skipped_perturbations.csv", index=False)
    (run_dir / "schema_report.json").write_text(
        json.dumps(schema_report.__dict__, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (run_dir / "dataset_preparation.json").write_text(
        json.dumps(preparation.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (run_dir / "dataset_registry.json").write_text(
        json.dumps(dataset_record.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    write_v04_strengthening_report(
        report_path=run_dir / "report.md",
        experiment_id=config["experiment_id"],
        dataset_id=dataset_record.dataset_id,
        output_dir=run_dir,
        git_commit=git_commit,
        metric_summary=metric_summary,
        repeated_metrics=metrics,
        retrieval_summary=retrieval_summary,
        de_summary=de_summary,
        skipped_perturbations=skipped_perturbations,
        benchmark_alignment="See docs/PUBLIC_BENCHMARK_ALIGNMENT_V04.md.",
        claim_boundary=config["reporting"]["claim_boundary"],
        limitations=config["reporting"]["limitations"],
    )
    print(run_dir)


def _evaluate_split(
    config: dict[str, Any],
    dataset,
    split: pd.Series,
    *,
    split_mode: str,
    repeat_id: int,
    seed: int,
    metric_rows: list[dict[str, Any]],
    retrieval_rows: list[dict[str, Any]],
    de_rows: list[dict[str, Any]],
    heldout_perturbation: str | None = None,
) -> None:
    train = subset_delta_dataset(dataset, split == "train")
    train_candidates = candidate_profiles_from_observed(train.observed_delta, train.metadata)
    for baseline in _baseline_instances(config["baselines"]):
        baseline.fit(train)
        for split_label in ("val", "test"):
            mask = split == split_label
            if not mask.any():
                continue
            query = subset_delta_dataset(dataset, mask)
            predicted_delta = baseline.predict_delta(query)
            metrics = evaluate_delta_predictions(query, predicted_delta)
            metric_rows.append(
                {
                    "split_mode": split_mode,
                    "split": split_label,
                    "repeat_id": repeat_id,
                    "seed": seed,
                    "heldout_perturbation": heldout_perturbation,
                    "baseline": baseline.name,
                    "n_examples": len(query.group_ids),
                    **metrics,
                }
            )
            retrieval = perturbation_retrieval_metrics(
                predicted_delta,
                query.metadata,
                train_candidates,
            )
            retrieval_summary = summarize_retrieval(retrieval)
            retrieval_rows.append(
                {
                    "split_mode": split_mode,
                    "split": split_label,
                    "repeat_id": repeat_id,
                    "seed": seed,
                    "heldout_perturbation": heldout_perturbation,
                    "baseline": baseline.name,
                    **retrieval_summary,
                }
            )
            for group_id in query.group_ids:
                row = de_recovery_metrics(
                    query.observed_delta.loc[group_id].to_numpy(dtype=float),
                    predicted_delta.loc[group_id].to_numpy(dtype=float),
                    ks=tuple(config["evaluation"]["de_ks"]),
                )
                row.update(
                    {
                        "split_mode": split_mode,
                        "split": split_label,
                        "repeat_id": repeat_id,
                        "seed": seed,
                        "heldout_perturbation": heldout_perturbation,
                        "baseline": baseline.name,
                        "group_id": group_id,
                    }
                )
                de_rows.append(row)


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
        elif name == "ridge":
            yield RidgeBaseline(alpha=float(config.get("alpha", 1.0)))
        elif name == "ridge_cv":
            yield RidgeCVBaseline(alphas=tuple(map(float, config.get("alphas", [0.1, 1.0, 10.0]))))
        else:
            raise ValueError(f"unsupported baseline: {name}")


def _retrieval_summary_table(retrieval: pd.DataFrame) -> pd.DataFrame:
    if retrieval.empty:
        return retrieval
    grouped = retrieval.groupby(["split_mode", "split", "baseline"], dropna=False).agg(
        n=("n", "sum"),
        top1_accuracy=("top1_accuracy", "mean"),
        mean_reciprocal_rank=("mean_reciprocal_rank", "mean"),
        underpowered=("underpowered", "max"),
    )
    return grouped.reset_index()


def _de_summary_table(de_metrics: pd.DataFrame) -> pd.DataFrame:
    if de_metrics.empty:
        return de_metrics
    metric_columns = [
        column
        for column in de_metrics.columns
        if column.startswith("top_") or column == "spearman_gene_rank"
    ]
    return (
        de_metrics.groupby(["split_mode", "split", "baseline"], dropna=False)[metric_columns]
        .mean(numeric_only=True)
        .reset_index()
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to v0.4 repeated baseline config.")
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
    return Path(config["output_root"]) / config["output_prefix"] / dataset_id / timestamp


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

