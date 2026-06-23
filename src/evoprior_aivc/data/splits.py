"""Split helpers and leakage checks for perturbation response benchmarks."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Literal

import numpy as np
import pandas as pd

SplitName = Literal["train", "val", "test"]


def assign_group_holdout_split(
    metadata: pd.DataFrame,
    holdout: Mapping[str, Iterable[object]],
    *,
    val_fraction: float = 0.2,
    seed: int = 0,
) -> pd.Series:
    """Assign train/val/test labels using explicit held-out metadata values.

    Rows matching any held-out value are assigned to ``test``. Remaining rows are
    randomly split into ``train`` and ``val`` with a deterministic seed.
    """
    if metadata.empty:
        raise ValueError("metadata must contain at least one row")
    if not 0.0 <= val_fraction < 1.0:
        raise ValueError("val_fraction must be in [0.0, 1.0)")
    if not holdout:
        raise ValueError("holdout must define at least one metadata column")

    test_mask = pd.Series(False, index=metadata.index)
    for column, values in holdout.items():
        if column not in metadata.columns:
            raise KeyError(f"holdout column is missing from metadata: {column}")
        value_set = set(values)
        if not value_set:
            raise ValueError(f"holdout values for column {column!r} must not be empty")
        test_mask |= metadata[column].isin(value_set)

    labels = pd.Series("train", index=metadata.index, dtype="object")
    labels.loc[test_mask] = "test"

    train_candidates = labels.index[labels == "train"].to_numpy()
    if train_candidates.size == 0:
        raise ValueError("holdout definition leaves no train/val candidates")

    val_count = int(np.floor(train_candidates.size * val_fraction))
    if val_count > 0:
        rng = np.random.default_rng(seed)
        val_index = rng.choice(train_candidates, size=val_count, replace=False)
        labels.loc[val_index] = "val"

    return labels.astype("category")


def assert_holdout_values_absent(
    metadata: pd.DataFrame,
    split: Sequence[str] | pd.Series,
    *,
    column: str,
    values: Iterable[object],
    train_like_labels: Iterable[str] = ("train", "val"),
) -> None:
    """Raise if held-out values appear in train-like split labels."""
    if column not in metadata.columns:
        raise KeyError(f"column is missing from metadata: {column}")

    split_series = _coerce_split(split, metadata.index)
    train_like = set(train_like_labels)
    value_set = set(values)
    train_like_mask = split_series.isin(train_like)
    leaked_values = set(metadata.loc[train_like_mask, column]).intersection(value_set)
    if leaked_values:
        leaked = ", ".join(sorted(map(str, leaked_values)))
        raise ValueError(f"held-out {column} values leaked into train/val: {leaked}")


def assert_no_forbidden_feature_columns(
    feature_columns: Iterable[str],
    *,
    forbidden_columns: Iterable[str],
) -> None:
    """Raise if feature columns include target/post-perturbation fields."""
    features = set(feature_columns)
    forbidden = set(forbidden_columns)
    leaked = features.intersection(forbidden)
    if leaked:
        leaked_list = ", ".join(sorted(leaked))
        raise ValueError(f"forbidden target-derived feature columns detected: {leaked_list}")


def _coerce_split(split: Sequence[str] | pd.Series, index: pd.Index) -> pd.Series:
    if isinstance(split, pd.Series):
        if not split.index.equals(index):
            split = split.reindex(index)
        return split.astype("object")
    if len(split) != len(index):
        raise ValueError("split length must match metadata length")
    return pd.Series(split, index=index, dtype="object")
