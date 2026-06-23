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
