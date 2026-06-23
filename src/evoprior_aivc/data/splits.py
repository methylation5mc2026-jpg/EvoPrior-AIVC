"""Split helpers and leakage checks for perturbation response benchmarks."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Literal

import numpy as np
import pandas as pd

SplitName = Literal["train", "val", "test"]


def assign_random_group_split(
    metadata: pd.DataFrame,
    *,
    val_fraction: float = 0.2,
    test_fraction: float = 0.2,
    seed: int = 0,
) -> pd.Series:
    """Assign train/val/test labels to pseudobulk groups at random."""
    if metadata.empty:
        raise ValueError("metadata must contain at least one row")
    if not 0.0 <= val_fraction < 1.0:
        raise ValueError("val_fraction must be in [0.0, 1.0)")
    if not 0.0 <= test_fraction < 1.0:
        raise ValueError("test_fraction must be in [0.0, 1.0)")
    if val_fraction + test_fraction >= 1.0:
        raise ValueError("val_fraction + test_fraction must be less than 1.0")

    rng = np.random.default_rng(seed)
    shuffled = np.array(metadata.index)
    rng.shuffle(shuffled)
    n_groups = shuffled.size
    n_test = int(np.floor(n_groups * test_fraction))
    n_val = int(np.floor(n_groups * val_fraction))

    labels = pd.Series("train", index=metadata.index, dtype="object")
    if n_test > 0:
        labels.loc[shuffled[:n_test]] = "test"
    if n_val > 0:
        labels.loc[shuffled[n_test : n_test + n_val]] = "val"
    return labels.astype("category")


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


def assign_heldout_cell_type_split(
    metadata: pd.DataFrame,
    *,
    heldout_cell_type: str,
    val_fraction: float = 0.0,
    seed: int = 0,
) -> pd.Series:
    """Assign train/val/test labels for one held-out cell type."""
    if "cell_type" not in metadata.columns:
        raise KeyError("metadata must contain a 'cell_type' column")
    if heldout_cell_type not in set(metadata["cell_type"].astype(str)):
        raise ValueError(f"heldout cell type has no groups: {heldout_cell_type}")
    return assign_group_holdout_split(
        metadata,
        {"cell_type": [heldout_cell_type]},
        val_fraction=val_fraction,
        seed=seed,
    )


def assign_heldout_lineage_split(
    metadata: pd.DataFrame,
    *,
    heldout_cell_types: Iterable[str],
    val_fraction: float = 0.0,
    seed: int = 0,
) -> pd.Series:
    """Assign split labels for a held-out lineage/clade represented by cell types."""
    cell_types = sorted(set(map(str, heldout_cell_types)))
    if not cell_types:
        raise ValueError("heldout_cell_types must not be empty")
    return assign_group_holdout_split(
        metadata,
        {"cell_type": cell_types},
        val_fraction=val_fraction,
        seed=seed,
    )


def heldout_cell_type_eligibility(
    pseudobulk_metadata: pd.DataFrame,
    *,
    control_label: str,
    min_test_groups: int = 3,
    min_control_groups: int = 1,
    min_train_groups: int = 3,
) -> pd.DataFrame:
    """Summarize whether each cell type can support held-out-cell-type evaluation."""
    required = {"cell_type", "perturbation"}
    missing = required.difference(pseudobulk_metadata.columns)
    if missing:
        raise KeyError(f"pseudobulk metadata missing columns: {', '.join(sorted(missing))}")
    rows: list[dict[str, object]] = []
    metadata = pseudobulk_metadata.copy()
    metadata["cell_type"] = metadata["cell_type"].astype(str)
    metadata["perturbation"] = metadata["perturbation"].astype(str)
    non_control = metadata["perturbation"] != control_label
    all_perturbations = set(metadata.loc[non_control, "perturbation"])

    for cell_type, group in metadata.groupby("cell_type", sort=True, observed=True):
        control_groups = group[group["perturbation"] == control_label]
        test_groups = group[group["perturbation"] != control_label]
        train_candidates = metadata[(metadata["cell_type"] != cell_type) & non_control]
        heldout_perturbations = set(test_groups["perturbation"])
        train_perturbations = set(train_candidates["perturbation"])
        shared = heldout_perturbations.intersection(train_perturbations)
        reasons = []
        if len(control_groups) < min_control_groups:
            reasons.append("too_few_control_groups")
        if len(test_groups) < min_test_groups:
            reasons.append("too_few_test_groups")
        if len(train_candidates) < min_train_groups:
            reasons.append("too_few_train_groups")
        if heldout_perturbations and not shared:
            reasons.append("no_train_overlap_for_heldout_perturbations")
        if not all_perturbations:
            reasons.append("no_non_control_perturbations")
        rows.append(
            {
                "cell_type": str(cell_type),
                "n_control_groups": int(len(control_groups)),
                "n_test_groups": int(len(test_groups)),
                "n_train_candidate_groups": int(len(train_candidates)),
                "n_heldout_perturbations": int(len(heldout_perturbations)),
                "n_shared_train_perturbations": int(len(shared)),
                "eligible": not reasons,
                "reason": "eligible" if not reasons else ";".join(reasons),
            }
        )
    return pd.DataFrame(rows).sort_values("cell_type", kind="mergesort").reset_index(drop=True)


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
