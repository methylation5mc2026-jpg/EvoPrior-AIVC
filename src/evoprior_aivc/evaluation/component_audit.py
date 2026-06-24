"""Component-level audits for integrated additive predictions."""

from __future__ import annotations

from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def component_magnitude_summary(components: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Summarize absolute and L2 component magnitudes."""
    rows = []
    for name, frame in components.items():
        if name == "final_delta":
            continue
        values = frame.to_numpy(dtype=float).ravel()
        rows.append(
            {
                "component": name,
                "mean_abs": float(np.mean(np.abs(values))) if values.size else 0.0,
                "max_abs": float(np.max(np.abs(values))) if values.size else 0.0,
                "l2": float(np.linalg.norm(values)) if values.size else 0.0,
            }
        )
    return pd.DataFrame(rows)


def component_correlation_summary(components: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Compute pairwise correlations between non-final components."""
    names = [name for name in components if name != "final_delta"]
    rows = []
    for left, right in combinations(names, 2):
        a = components[left].to_numpy(dtype=float).ravel()
        b = components[right].to_numpy(dtype=float).ravel()
        if a.size == 0 or b.size == 0 or np.std(a) == 0.0 or np.std(b) == 0.0:
            corr = np.nan
        else:
            corr = float(np.corrcoef(a, b)[0, 1])
        rows.append({"left": left, "right": right, "pearson": corr})
    return pd.DataFrame(rows)


def top_component_genes(frame: pd.DataFrame, *, n: int = 20) -> pd.DataFrame:
    """Return genes with largest mean absolute component values."""
    values = frame.abs().mean(axis=0).sort_values(ascending=False).head(n)
    return pd.DataFrame(
        {"gene": values.index.astype(str), "mean_abs": values.to_numpy(dtype=float)}
    )


def write_component_audit_report(
    path: Path,
    *,
    title: str,
    components: dict[str, pd.DataFrame],
    shuffled_components: dict[str, pd.DataFrame] | None = None,
    claim_boundary: str,
    n_top: int = 20,
) -> dict[str, Any]:
    """Write a markdown component audit and return a compact summary."""
    path.parent.mkdir(parents=True, exist_ok=True)
    magnitudes = component_magnitude_summary(components)
    correlations = component_correlation_summary(components)
    gene_prior = components.get("gene_prior_component", pd.DataFrame())
    lineage = components.get("lineage_component", pd.DataFrame())
    gene_prior_mean_abs = _component_mean_abs(gene_prior)
    lineage_mean_abs = _component_mean_abs(lineage)
    shuffled_gene_prior_mean_abs = None
    if shuffled_components is not None:
        shuffled_gene_prior_mean_abs = _component_mean_abs(
            shuffled_components.get("gene_prior_component", pd.DataFrame())
        )
    summary = {
        "gene_prior_mean_abs": gene_prior_mean_abs,
        "lineage_mean_abs": lineage_mean_abs,
        "gene_prior_collapsed": gene_prior_mean_abs < 1e-12,
        "mostly_lineage": lineage_mean_abs > gene_prior_mean_abs,
        "shuffled_gene_prior_mean_abs": shuffled_gene_prior_mean_abs,
    }
    lines = [
        f"# {title}",
        "",
        "## Claim Boundary",
        "",
        claim_boundary,
        "",
        "## Magnitudes",
        "",
        _markdown_table(magnitudes),
        "",
        "## Correlations",
        "",
        _markdown_table(correlations),
        "",
        "## Top Gene-Prior Component Genes",
        "",
        _markdown_table(top_component_genes(gene_prior, n=n_top))
        if not gene_prior.empty
        else "none",
        "",
        "## Top Lineage Component Genes",
        "",
        _markdown_table(top_component_genes(lineage, n=n_top)) if not lineage.empty else "none",
        "",
        "## Summary Flags",
        "",
        _markdown_table(pd.DataFrame([summary])),
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return summary


def _component_mean_abs(frame: pd.DataFrame) -> float:
    if frame.empty:
        return 0.0
    return float(np.mean(np.abs(frame.to_numpy(dtype=float))))


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
