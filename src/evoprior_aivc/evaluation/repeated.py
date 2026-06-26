"""Repeated evaluation helpers."""

from __future__ import annotations

import pandas as pd


def repeated_seeds(start: int, n_repeats: int) -> list[int]:
    """Return deterministic consecutive seeds."""
    if n_repeats <= 0:
        raise ValueError("n_repeats must be positive")
    return [int(start) + idx for idx in range(int(n_repeats))]


def perturbations_with_min_groups(
    metadata: pd.DataFrame,
    *,
    perturbation_column: str = "perturbation",
    min_test_groups: int = 2,
) -> tuple[list[str], pd.DataFrame]:
    """Return perturbations eligible for leave-one-perturbation evaluation."""
    counts = metadata[perturbation_column].value_counts()
    eligible = sorted(map(str, counts[counts >= min_test_groups].index))
    skipped_rows = [
        {
            "perturbation": str(perturbation),
            "n_groups": int(n_groups),
            "reason": f"fewer than min_test_groups={min_test_groups}",
        }
        for perturbation, n_groups in counts.items()
        if n_groups < min_test_groups
    ]
    return eligible, pd.DataFrame(skipped_rows)

