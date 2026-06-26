"""Shared data structures for baseline perturbation-response models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class DeltaDataset:
    """Matched-control pseudobulk examples for delta prediction."""

    group_ids: tuple[str, ...]
    metadata: pd.DataFrame
    control_expression: pd.DataFrame
    observed_post_expression: pd.DataFrame
    observed_delta: pd.DataFrame

    @property
    def gene_names(self) -> list[str]:
        return list(map(str, self.observed_delta.columns))


def build_delta_dataset(
    expression: pd.DataFrame,
    metadata: pd.DataFrame,
    *,
    control_label: str = "control",
    match_columns: tuple[str, ...] = ("cell_type", "donor"),
    fallback: Literal["raise", "global"] = "raise",
) -> DeltaDataset:
    """Build non-control delta examples from pseudobulk profiles."""
    _validate_expression_metadata(expression, metadata)
    if "perturbation" not in metadata.columns:
        raise KeyError("metadata must contain a 'perturbation' column")
    missing_match = [column for column in match_columns if column not in metadata.columns]
    if missing_match:
        missing = ", ".join(missing_match)
        raise KeyError(f"metadata is missing match columns: {missing}")

    control_mask = metadata["perturbation"] == control_label
    if not control_mask.any():
        raise ValueError(f"no control pseudobulk rows found for label {control_label!r}")

    global_control = expression.loc[control_mask].mean(axis=0)
    control_lookup: dict[tuple[object, ...], np.ndarray] = {}
    control_groups = metadata.loc[control_mask].groupby(list(match_columns), dropna=False)
    for key, group_index in control_groups.groups.items():
        if not isinstance(key, tuple):
            key = (key,)
        control_lookup[key] = expression.loc[group_index].mean(axis=0).to_numpy(dtype=float)

    rows: list[str] = []
    control_rows: list[np.ndarray] = []
    post_rows: list[np.ndarray] = []
    meta_rows: list[pd.Series] = []

    for group_id, row in metadata.loc[~control_mask].iterrows():
        key = tuple(row[column] for column in match_columns)
        control = control_lookup.get(key)
        if control is None:
            if fallback == "raise":
                key_text = ", ".join(map(str, key))
                raise ValueError(f"no matched control found for group {group_id}: {key_text}")
            if fallback == "global":
                control = global_control.to_numpy(dtype=float)
            else:
                raise ValueError("fallback must be 'raise' or 'global'")

        rows.append(str(group_id))
        control_rows.append(control)
        post_rows.append(expression.loc[group_id].to_numpy(dtype=float))
        meta_rows.append(row)

    control_df = pd.DataFrame(control_rows, index=rows, columns=expression.columns, dtype=float)
    post_df = pd.DataFrame(post_rows, index=rows, columns=expression.columns, dtype=float)
    metadata_df = pd.DataFrame(meta_rows, index=rows)
    delta_df = post_df - control_df
    return DeltaDataset(
        group_ids=tuple(rows),
        metadata=metadata_df,
        control_expression=control_df,
        observed_post_expression=post_df,
        observed_delta=delta_df,
    )


class DeltaBaseline:
    """Minimal estimator protocol for deterministic delta baselines."""

    name: str = "baseline"

    def fit(self, dataset: DeltaDataset) -> DeltaBaseline:
        raise NotImplementedError

    def predict_delta(self, dataset: DeltaDataset) -> pd.DataFrame:
        raise NotImplementedError

    def predict_post_expression(self, dataset: DeltaDataset) -> pd.DataFrame:
        return dataset.control_expression + self.predict_delta(dataset)


def zeros_like_delta(dataset: DeltaDataset) -> pd.DataFrame:
    """Return a zero-delta DataFrame matching a dataset."""
    return pd.DataFrame(
        np.zeros_like(dataset.observed_delta.to_numpy(dtype=float)),
        index=dataset.observed_delta.index,
        columns=dataset.observed_delta.columns,
        dtype=float,
    )


def _validate_expression_metadata(expression: pd.DataFrame, metadata: pd.DataFrame) -> None:
    if expression.empty:
        raise ValueError("expression must not be empty")
    if metadata.empty:
        raise ValueError("metadata must not be empty")
    if not expression.index.equals(metadata.index):
        raise ValueError("expression and metadata indexes must match exactly")

