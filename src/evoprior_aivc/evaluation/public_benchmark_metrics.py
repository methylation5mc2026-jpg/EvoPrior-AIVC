"""Public-benchmark-compatible reporting helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


def split_leakage_audit(split_manifest: pd.DataFrame) -> dict[str, Any]:
    """Audit a leave-one-perturbation split manifest for train/val leakage."""
    required = {"heldout_perturbation", "split", "perturbation"}
    missing = required.difference(split_manifest.columns)
    if missing:
        raise KeyError(f"split manifest missing columns: {', '.join(sorted(missing))}")
    rows: list[dict[str, Any]] = []
    overall_pass = True
    for heldout, group in split_manifest.groupby("heldout_perturbation", dropna=False):
        heldout_value = str(heldout)
        train_like = group[group["split"].isin(["train", "val"])]
        leaked = sorted(
            set(train_like["perturbation"].astype(str)).intersection({heldout_value})
        )
        passed = not leaked
        overall_pass = overall_pass and passed
        rows.append(
            {
                "heldout_perturbation": heldout_value,
                "train_val_leakage_pass": passed,
                "leaked_perturbations": leaked,
                "n_train": int((group["split"] == "train").sum()),
                "n_val": int((group["split"] == "val").sum()),
                "n_test": int((group["split"] == "test").sum()),
                "train_perturbations": sorted(
                    set(group.loc[group["split"] == "train", "perturbation"].astype(str))
                ),
                "val_perturbations": sorted(
                    set(group.loc[group["split"] == "val", "perturbation"].astype(str))
                ),
                "test_perturbations": sorted(
                    set(group.loc[group["split"] == "test", "perturbation"].astype(str))
                ),
            }
        )
    return {"overall_pass": overall_pass, "rows": rows}


def split_size_table(split_manifest: pd.DataFrame) -> pd.DataFrame:
    """Return train/val/test sizes per held-out perturbation."""
    if split_manifest.empty:
        return pd.DataFrame()
    return (
        split_manifest.groupby(["heldout_perturbation", "split"], dropna=False)
        .agg(n_groups=("group_id", "count"), n_cells=("n_cells", "sum"))
        .reset_index()
        .sort_values(["heldout_perturbation", "split"], kind="mergesort")
    )


def write_split_report(
    path: Path,
    *,
    split_manifest: pd.DataFrame,
    split_type: str,
    alignment_status: str,
    official_aligned: bool,
) -> dict[str, Any]:
    """Write a markdown split report and return the leakage audit."""
    audit = split_leakage_audit(split_manifest)
    size_table = split_size_table(split_manifest)
    all_perturbations = sorted(set(split_manifest["perturbation"].astype(str)))
    heldouts = sorted(set(split_manifest["heldout_perturbation"].astype(str)))
    lines = [
        "# v0.12 Split Report",
        "",
        f"- Split type: `{split_type}`",
        f"- Alignment status: `{alignment_status}`",
        f"- Official aligned: `{official_aligned}`",
        f"- Train/validation leakage audit pass: `{audit['overall_pass']}`",
        f"- Perturbations total: {len(all_perturbations)}",
        f"- Held-out perturbations evaluated: {len(heldouts)}",
        "",
        "## Train/Val/Test Sizes",
        "",
        _markdown_table(size_table),
        "",
        "## Held-Out Perturbation Overlap Checks",
        "",
        _markdown_table(pd.DataFrame(audit["rows"])),
        "",
        "## Claim Status",
        "",
        (
            "This split can be described as official-aligned."
            if official_aligned
            else (
                "This split is custom benchmark-compatible and must not be described as "
                "an official split."
            )
        ),
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    (path.parent / "split_leakage_audit.json").write_text(
        json.dumps(audit, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return audit


def write_public_benchmark_report(
    path: Path,
    *,
    config: dict[str, Any],
    run_dir: Path,
    data_report_dir: Path,
    dataset_preparation: dict[str, Any],
    metric_summary: pd.DataFrame,
    per_run_metrics: pd.DataFrame,
    de_summary: pd.DataFrame,
    retrieval_summary: pd.DataFrame,
    split_audit: dict[str, Any],
    skipped_perturbations: pd.DataFrame,
) -> None:
    """Write the v0.12 public benchmark baseline report."""
    benchmark = config["benchmark"]
    reporting = config["reporting"]
    lines = [
        "# v0.12 Public Benchmark Baseline Run",
        "",
        "## Executive Summary",
        "",
        (
            "A reproducible baseline run was executed on a public scPerturb-compatible "
            "Papalexi/Satija H5AD using a documented custom leave-one-perturbation split."
        ),
        "",
        "## Benchmark Selected And Why",
        "",
        f"- Benchmark ID: `{config['benchmark_id']}`",
        f"- Dataset ID: `{config['dataset_id']}`",
        f"- Selection: {benchmark['selected_benchmark']}",
        (
            "- Rationale: local public H5AD exists, checksum is locked, and the run "
            "can execute today without a large uncontrolled download."
        ),
        "",
        "## Official/Compatible/Custom Alignment Status",
        "",
        f"- Status: `{benchmark['official_alignment_status']}`",
        f"- Notes: {benchmark['official_alignment_notes']}",
        "",
        "## Dataset Source And Checksum",
        "",
        f"- Source: {benchmark['source']}",
        f"- Version/access: {benchmark['source_version']}",
        f"- Local path: `{dataset_preparation.get('path')}`",
        f"- Checksum status: `{dataset_preparation.get('checksum_status')}`",
        "",
        "## Schema Mapping",
        "",
        f"- Schema report directory: `{data_report_dir}`",
        "",
        "## Split Definition",
        "",
        f"- Split: {benchmark['split_definition']}",
        f"- Leakage audit pass: `{split_audit['overall_pass']}`",
        "",
        "## Leakage Audit",
        "",
        _markdown_table(pd.DataFrame(split_audit["rows"])),
        "",
        "## Baselines",
        "",
        "\n".join(f"- `{item['name']}`" for item in config["baselines"]),
        "",
        "## Metrics",
        "",
        f"- Metric status: {benchmark['metric_status']}",
        (
            "- Locked metrics: MAE, MSE, Pearson delta correlation, Spearman logFC, "
            "and DE top-k recovery."
        ),
        "",
        "## Main Result Table",
        "",
        _markdown_table(metric_summary),
        "",
        "## Per-Perturbation Or Per-Class Breakdown",
        "",
        _markdown_table(per_run_metrics.head(80)),
        "",
        "## DE Recovery",
        "",
        _markdown_table(de_summary),
        "",
        "## Retrieval/PDS-Compatible Checks",
        "",
        _markdown_table(retrieval_summary),
        "",
        "## Failure Cases",
        "",
        _markdown_table(skipped_perturbations)
        if not skipped_perturbations.empty
        else (
            "No perturbations were skipped by the configured minimum group "
            "threshold."
        ),
        "",
        "## What Can Be Externally Claimed",
        "",
        (
            "- We executed a reproducible baseline run on a public "
            "scPerturb-compatible Papalexi/Satija dataset using documented data, "
            "split, and internal compatible metrics."
        ),
        (
            "- Baseline metrics can be quoted only under this exact custom split, "
            "preprocessing, and metric script."
        ),
        "",
        "## What Cannot Be Claimed",
        "",
        "- No SOTA or leaderboard claim.",
        "- No official benchmark claim.",
        "- No biological discovery claim.",
        "- No general EvoPrior superiority claim.",
        "",
        "## Next Steps Toward Industry-Recognized Result",
        "",
        "- Import an official GEARS/Norman or comparable public split when legally available.",
        "- Match official metric scripts before claiming leaderboard comparability.",
        "- Package data provenance, split manifest, and run artifacts for external review.",
        "",
        "## Claim Boundary",
        "",
        reporting["claim_boundary"],
        "",
        "## Output Directory",
        "",
        f"`{run_dir}`",
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
        values = [_format_cell(row[column]) for column in frame.columns]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def _format_cell(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.6g}"
    if isinstance(value, list):
        return ", ".join(map(str, value))
    return str(value)
