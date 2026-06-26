"""Audits for gene-prior correction runs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from evoprior_aivc.priors.gene_prior_table import GenePriorTable

FORBIDDEN_PRIOR_FEATURE_TOKENS: tuple[str, ...] = (
    "observed_delta",
    "target_delta",
    "post_perturbation",
    "test_response",
    "heldout_metric",
)


def assert_gene_prior_features_do_not_use_response_labels(feature_columns: list[str]) -> None:
    """Reject feature columns that appear to encode response labels or metrics."""
    lower = [str(column).lower() for column in feature_columns]
    leaks = [
        column
        for column in lower
        if any(token in column for token in FORBIDDEN_PRIOR_FEATURE_TOKENS)
    ]
    if leaks:
        raise ValueError("gene-prior feature columns look response-derived: " + ", ".join(leaks))


def shuffled_prior_preserves_marginals(
    original: GenePriorTable,
    shuffled: GenePriorTable,
    *,
    numeric_columns: tuple[str, ...] = (
        "conservation_score",
        "ortholog_count",
        "expression_breadth",
    ),
) -> bool:
    """Return True when shuffled control preserves numeric marginal distributions."""
    left = original.to_dataframe()
    right = shuffled.to_dataframe()
    for column in numeric_columns:
        if column not in left.columns or column not in right.columns:
            continue
        a = sorted(pd.to_numeric(left[column], errors="coerce").dropna().tolist())
        b = sorted(pd.to_numeric(right[column], errors="coerce").dropna().tolist())
        if not np.allclose(a, b, equal_nan=True):
            return False
    return True


def correction_magnitude_summary(correction: pd.Series | pd.DataFrame) -> dict[str, float | int]:
    """Summarize correction magnitudes for audit reports."""
    values = correction.to_numpy(dtype=float).ravel()
    abs_values = np.abs(values)
    return {
        "n_values": int(values.size),
        "mean_abs": float(abs_values.mean()) if values.size else 0.0,
        "max_abs": float(abs_values.max()) if values.size else 0.0,
        "p95_abs": float(np.quantile(abs_values, 0.95)) if values.size else 0.0,
    }


def top_corrected_genes(correction: pd.Series, *, n: int = 20) -> pd.DataFrame:
    """Return the largest absolute gene-level corrections."""
    ordered = correction.abs().sort_values(ascending=False).head(n)
    return pd.DataFrame(
        {
            "gene": ordered.index.astype(str),
            "correction": correction.loc[ordered.index].to_numpy(dtype=float),
            "abs_correction": ordered.to_numpy(dtype=float),
        }
    )


def write_prior_audit_report(
    path: Path,
    *,
    title: str,
    source_summary: dict[str, Any],
    coverage_summary: dict[str, Any],
    feature_columns: list[str],
    shuffled_preserves_marginals: bool,
    correction_summary: dict[str, Any],
    top_genes: pd.DataFrame,
    claim_boundary: str,
) -> None:
    """Write a compact markdown audit report."""
    lines = [
        f"# {title}",
        "",
        "## Claim Boundary",
        "",
        claim_boundary,
        "",
        "## Source Summary",
        "",
        *_dict_lines(source_summary),
        "",
        "## Coverage Summary",
        "",
        *_dict_lines(coverage_summary),
        "",
        "## Feature Columns",
        "",
        *_list_lines(feature_columns),
        "",
        "## Shuffled Control",
        "",
        f"- Preserves numeric marginals: {shuffled_preserves_marginals}",
        "",
        "## Correction Magnitude",
        "",
        *_dict_lines(correction_summary),
        "",
        "## Top Corrected Genes",
        "",
        _markdown_table(top_genes),
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def _dict_lines(payload: dict[str, Any]) -> list[str]:
    if not payload:
        return ["- none"]
    return [f"- `{key}`: {value}" for key, value in payload.items()]


def _list_lines(items: list[str]) -> list[str]:
    return [f"- `{item}`" for item in items] if items else ["- none"]


def _markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "No rows."
    columns = list(map(str, frame.columns))
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for _, row in frame.iterrows():
        lines.append("| " + " | ".join(str(row[column]) for column in frame.columns) + " |")
    return "\n".join(lines)
