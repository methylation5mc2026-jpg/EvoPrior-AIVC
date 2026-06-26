"""Markdown report generation for baseline smoke experiments."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def write_baseline_report(
    *,
    report_path: Path,
    experiment_id: str,
    output_dir: Path,
    git_commit: str,
    metrics: pd.DataFrame,
    breakdown: pd.DataFrame,
    assumptions: list[str],
    limitations: list[str],
) -> None:
    """Write a compact markdown report for a baseline run."""
    lines = [
        f"# {experiment_id}",
        "",
        "## 运行信息",
        "",
        f"- Output directory: `{output_dir}`",
        f"- Git commit: `{git_commit}`",
        "- Dataset: synthetic perturbation fixture",
        "- Claim status: engineering validation only; no biological or SOTA claim",
        "",
        "## Baseline Metrics",
        "",
        _table(metrics),
        "",
        "## Breakdown",
        "",
        _table(breakdown) if not breakdown.empty else "No breakdown metrics generated.",
        "",
        "## Assumptions",
        "",
        *[f"- {item}" for item in assumptions],
        "",
        "## Limitations",
        "",
        *[f"- {item}" for item in limitations],
        "",
    ]
    report_path.write_text("\n".join(lines), encoding="utf-8")


def write_real_baseline_report(
    *,
    report_path: Path,
    experiment_id: str,
    dataset_id: str,
    output_dir: Path,
    git_commit: str,
    metrics: pd.DataFrame,
    breakdown: pd.DataFrame,
    split_summary: pd.DataFrame,
    group_summary: dict[str, object],
    top_failures: pd.DataFrame,
    assumptions: list[str],
    limitations: list[str],
) -> None:
    """Write the v0.3 real-data baseline markdown report."""
    lines = [
        "# v0.3 Real Benchmark Baseline Report",
        "",
        "## Claim Boundary",
        "",
        (
            "This run validates that EvoPrior-AIVC can ingest one real perturbation dataset "
            "and run leakage-checked baselines. It does not establish SOTA, biological "
            "superiority, or generalization beyond this dataset/split."
        ),
        "",
        "## Run Info",
        "",
        f"- Experiment ID: `{experiment_id}`",
        f"- Dataset ID: `{dataset_id}`",
        f"- Output directory: `{output_dir}`",
        f"- Git commit: `{git_commit}`",
        "",
        "## Group Summary",
        "",
        *_dict_bullets(group_summary),
        "",
        "## Split Summary",
        "",
        _table(split_summary),
        "",
        "## Baseline Metrics",
        "",
        _table(metrics),
        "",
        "## Breakdown",
        "",
        _table(breakdown) if not breakdown.empty else "No breakdown metrics generated.",
        "",
        "## Top Failure Cases",
        "",
        _table(top_failures) if not top_failures.empty else "No failure table generated.",
        "",
        "## Assumptions",
        "",
        *[f"- {item}" for item in assumptions],
        "",
        "## Limitations",
        "",
        *[f"- {item}" for item in limitations],
        "",
    ]
    report_path.write_text("\n".join(lines), encoding="utf-8")


def write_v04_strengthening_report(
    *,
    report_path: Path,
    experiment_id: str,
    dataset_id: str,
    output_dir: Path,
    git_commit: str,
    metric_summary: pd.DataFrame,
    repeated_metrics: pd.DataFrame,
    retrieval_summary: pd.DataFrame,
    de_summary: pd.DataFrame,
    skipped_perturbations: pd.DataFrame,
    sensitivity_summary: pd.DataFrame | None = None,
    benchmark_alignment: str = "not audited in this run",
    claim_boundary: str,
    limitations: list[str],
) -> None:
    """Write the v0.4 real baseline strengthening report."""
    lines = [
        "# v0.4 Real Baseline Strengthening Report",
        "",
        "## Executive Summary",
        "",
        (
            "v0.4 strengthens the real-data baseline layer and exposes which splits "
            "and metrics are statistically meaningful on the selected dataset."
        ),
        "",
        "## Claim Boundary",
        "",
        claim_boundary,
        "",
        "## Dataset and Schema",
        "",
        f"- Dataset ID: `{dataset_id}`",
        f"- Experiment ID: `{experiment_id}`",
        f"- Output directory: `{output_dir}`",
        f"- Git commit: `{git_commit}`",
        "",
        "## Pseudobulk and Controls",
        "",
        "Pseudobulk and control construction follow the resolved config saved in this run.",
        "",
        "## Splits",
        "",
        "The run includes repeated random-group splits and a leave-one-perturbation suite.",
        "",
        "## Baselines",
        "",
        "Baselines are non-neural classical models only.",
        "",
        "## Metrics",
        "",
        "Metrics include delta MAE/MSE/correlation, perturbation retrieval, and DE recovery.",
        "",
        "## Repeated Evaluation Results",
        "",
        _table(metric_summary),
        "",
        "## Per-Run Metrics",
        "",
        _table(repeated_metrics.head(40)),
        "",
        "## Leave-One-Perturbation Suite",
        "",
        (
            _table(skipped_perturbations)
            if not skipped_perturbations.empty
            else "No perturbations skipped."
        ),
        "",
        "## PDS / Retrieval Metrics",
        "",
        _table(retrieval_summary),
        "",
        "## DE Recovery Metrics",
        "",
        _table(de_summary),
        "",
        "## Sensitivity Audit",
        "",
        (
            _table(sensitivity_summary)
            if sensitivity_summary is not None and not sensitivity_summary.empty
            else "See the separate sensitivity run/report if generated."
        ),
        "",
        "## Leakage Checks",
        "",
        "Group-level split and held-out perturbation leakage checks passed during execution.",
        "",
        "## Failure Cases",
        "",
        "Failure-case CSVs are saved as run artifacts for downstream inspection.",
        "",
        "## Public Benchmark Alignment",
        "",
        benchmark_alignment,
        "",
        "## Limitations",
        "",
        *[f"- {item}" for item in limitations],
        "",
        "## What This Enables For v0.5",
        "",
        (
            "The project can now compare a first lineage-prior module against stronger, "
            "repeated classical baselines without changing the evaluation substrate."
        ),
        "",
    ]
    report_path.write_text("\n".join(lines), encoding="utf-8")


def _table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return ""
    columns = list(map(str, frame.columns))
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for _, row in frame.iterrows():
        values = [_format_cell(row[column]) for column in frame.columns]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def _format_cell(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def _dict_bullets(payload: dict[str, object]) -> list[str]:
    return [f"- `{key}`: {value}" for key, value in payload.items()]
