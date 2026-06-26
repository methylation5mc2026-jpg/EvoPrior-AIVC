"""Small statistical summaries for repeated evaluations."""

from __future__ import annotations

import math
from collections.abc import Iterable

import numpy as np
import pandas as pd


def normal_approx_ci(
    values: Iterable[float],
    *,
    confidence: float = 0.95,
) -> dict[str, float | int | bool | None]:
    """Return mean/std/normal-approximation CI with underpowered flag."""
    series = pd.Series(list(values), dtype="float64").dropna()
    n = int(series.shape[0])
    if n == 0:
        return {
            "n": 0,
            "mean": None,
            "std": None,
            "ci_low": None,
            "ci_high": None,
            "underpowered": True,
        }
    mean = float(series.mean())
    if n == 1:
        return {
            "n": n,
            "mean": mean,
            "std": 0.0,
            "ci_low": None,
            "ci_high": None,
            "underpowered": True,
        }
    z = _z_value(confidence)
    std = float(series.std(ddof=1))
    half_width = z * std / math.sqrt(n)
    return {
        "n": n,
        "mean": mean,
        "std": std,
        "ci_low": mean - half_width,
        "ci_high": mean + half_width,
        "underpowered": n < 3,
    }


def summarize_metric_table(
    metrics: pd.DataFrame,
    *,
    group_columns: tuple[str, ...],
    metric_columns: tuple[str, ...],
) -> pd.DataFrame:
    """Summarize repeated metric rows by group columns."""
    rows: list[dict[str, object]] = []
    for group_key, group in metrics.groupby(list(group_columns), dropna=False):
        if not isinstance(group_key, tuple):
            group_key = (group_key,)
        base = {column: value for column, value in zip(group_columns, group_key, strict=True)}
        for metric in metric_columns:
            summary = normal_approx_ci(group[metric])
            rows.append({**base, "metric": metric, **summary})
    return pd.DataFrame(rows)


def _z_value(confidence: float) -> float:
    if not np.isclose(confidence, 0.95):
        raise ValueError("only confidence=0.95 is currently supported")
    return 1.96

