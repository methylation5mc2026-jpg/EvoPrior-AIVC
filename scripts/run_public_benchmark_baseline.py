"""Run the v0.12 public-benchmark-compatible baseline benchmark."""

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
    build_delta_dataset,
)
from evoprior_aivc.data.adapters import write_schema_report
from evoprior_aivc.data.download import prepare_dataset
from evoprior_aivc.data.preprocess import preprocess_adata
from evoprior_aivc.data.pseudobulk import aggregate_pseudobulk
from evoprior_aivc.data.real_loader import load_real_dataset
from evoprior_aivc.data.splits import assign_group_holdout_split
from evoprior_aivc.evaluation.benchmark_evidence import collect_run_evidence, write_evidence_outputs
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
from evoprior_aivc.evaluation.public_benchmark_metrics import (
    write_public_benchmark_report,
    write_split_report,
)
from evoprior_aivc.evaluation.repeated import perturbations_with_min_groups
from evoprior_aivc.evaluation.statistics import summarize_metric_table
from evoprior_aivc.models import EvoPriorAdditiveModel


def main() -> None:
    args = _parse_args()
    config = _load_yaml(Path(args.config))
    run_dir = _make_run_dir(config)
    run_dir.mkdir(parents=True, exist_ok=False)
    _write_yaml(run_dir / "resolved_config.yaml", config)

    data_config_payload = _load_yaml(Path(config["data_config"]))
    data_config = data_config_payload.get("data", data_config_payload)
    benchmark_config = data_config_payload.get("benchmark", {})
    preparation = prepare_dataset(data_config)
    adata, schema_report = load_real_dataset(data_config)
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

    timestamp = run_dir.name
    data_report_dir = Path("outputs/data_reports") / config["benchmark_id"] / timestamp
    write_schema_report(schema_report, data_report_dir)
    write_schema_report(schema_report, run_dir)

    metrics, retrieval, de_metrics, split_manifest, skipped = _evaluate_leave_one_suite(
        config,
        dataset,
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
    split_manifest.to_csv(run_dir / "split_manifest.csv", index=False)
    split_manifest.to_csv(data_report_dir / "split_manifest.csv", index=False)
    skipped.to_csv(run_dir / "skipped_perturbations.csv", index=False)
    _write_json(run_dir / "schema_report.json", schema_report.__dict__)
    _write_json(run_dir / "dataset_preparation.json", preparation.to_dict())
    _write_json(run_dir / "public_benchmark_selection.json", benchmark_config)
    _write_json(
        run_dir / "run_manifest.json",
        {
            "git_commit": _git_commit(),
            "experiment_id": config["experiment_id"],
            "benchmark_id": config["benchmark_id"],
            "dataset_id": config["dataset_id"],
            "command": (
                "python scripts/run_public_benchmark_baseline.py --config "
                "configs/experiment/public_benchmark_v012_baseline.yaml"
            ),
            "data_source": config["benchmark"]["source"],
            "data_checksum": data_config["dataset"]["checksum"],
            "data_checksum_algorithm": data_config["dataset"]["checksum_algorithm"],
            "split_definition": config["benchmark"]["split_definition"],
            "metric_script": "src/evoprior_aivc/evaluation/public_benchmark_metrics.py",
            "alignment_status": config["benchmark"]["official_alignment_status"],
            "claim_boundary": config["reporting"]["claim_boundary"],
        },
    )
    split_audit = write_split_report(
        data_report_dir / "split_report.md",
        split_manifest=split_manifest,
        split_type="leave_one_perturbation_suite",
        alignment_status=config["benchmark"]["official_alignment_status"],
        official_aligned=False,
    )
    write_split_report(
        run_dir / "split_report.md",
        split_manifest=split_manifest,
        split_type="leave_one_perturbation_suite",
        alignment_status=config["benchmark"]["official_alignment_status"],
        official_aligned=False,
    )
    write_public_benchmark_report(
        run_dir / "report.md",
        config=config,
        run_dir=run_dir,
        data_report_dir=data_report_dir,
        dataset_preparation=preparation.to_dict(),
        metric_summary=metric_summary,
        per_run_metrics=metrics,
        de_summary=de_summary,
        retrieval_summary=retrieval_summary,
        split_audit=split_audit,
        skipped_perturbations=skipped,
    )
    records = collect_run_evidence(run_dir, config_path=args.config)
    write_evidence_outputs(records, run_dir, title="v0.12 Public Benchmark Evidence")
    print(run_dir)


def _evaluate_leave_one_suite(config: dict[str, Any], dataset):
    suite = config["evaluation"]["leave_one_perturbation_suite"]
    eligible, skipped = perturbations_with_min_groups(
        dataset.metadata,
        min_test_groups=int(suite["min_test_groups"]),
    )
    metric_rows: list[dict[str, Any]] = []
    retrieval_rows: list[dict[str, Any]] = []
    de_rows: list[dict[str, Any]] = []
    split_frames: list[pd.DataFrame] = []
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
        split_frames.append(_split_manifest(dataset.metadata, split, perturbation))
        _evaluate_split(
            config,
            dataset,
            split,
            split_mode="leave_one_perturbation_suite",
            repeat_id=repeat_id,
            seed=int(suite["seed"]) + repeat_id,
            heldout_perturbation=str(perturbation),
            metric_rows=metric_rows,
            retrieval_rows=retrieval_rows,
            de_rows=de_rows,
        )
    split_manifest = pd.concat(split_frames, ignore_index=True) if split_frames else pd.DataFrame()
    return (
        pd.DataFrame(metric_rows),
        pd.DataFrame(retrieval_rows),
        pd.DataFrame(de_rows),
        split_manifest,
        skipped,
    )


def _evaluate_split(
    config: dict[str, Any],
    dataset,
    split: pd.Series,
    *,
    split_mode: str,
    repeat_id: int,
    seed: int,
    heldout_perturbation: str,
    metric_rows: list[dict[str, Any]],
    retrieval_rows: list[dict[str, Any]],
    de_rows: list[dict[str, Any]],
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
                    "generalization_class": config["evaluation"]["generalization_class"],
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
        elif name == "ridge_cv":
            yield RidgeCVBaseline(alphas=tuple(map(float, config.get("alphas", [0.1, 1.0, 10.0]))))
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


def _split_manifest(
    metadata: pd.DataFrame,
    split: pd.Series,
    heldout_perturbation: str,
) -> pd.DataFrame:
    frame = metadata.copy()
    frame.insert(0, "group_id", frame.index.astype(str))
    frame.insert(1, "heldout_perturbation", str(heldout_perturbation))
    frame.insert(2, "split", split.astype(str).to_numpy())
    return frame.reset_index(drop=True)


def _retrieval_summary_table(retrieval: pd.DataFrame) -> pd.DataFrame:
    if retrieval.empty:
        return retrieval
    return (
        retrieval.groupby(["split_mode", "split", "baseline"], dropna=False)
        .agg(
            n=("n", "sum"),
            top1_accuracy=("top1_accuracy", "mean"),
            mean_reciprocal_rank=("mean_reciprocal_rank", "mean"),
            underpowered=("underpowered", "max"),
        )
        .reset_index()
    )


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
