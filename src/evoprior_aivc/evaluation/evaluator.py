"""Evaluation helpers for baseline prediction frames."""

from __future__ import annotations

import math
from collections.abc import Iterable

import pandas as pd

from evoprior_aivc.baselines.base import DeltaDataset
from evoprior_aivc.evaluation.metrics import (
    mean_absolute_error,
    mean_squared_error,
    pearson_delta_correlation,
    spearman_logfc_correlation,
)


def evaluate_delta_predictions(
    dataset: DeltaDataset,
    predicted_delta: pd.DataFrame,
) -> dict[str, float]:
    """Compute locked scalar metrics for delta predictions."""
    predicted_delta = predicted_delta.loc[dataset.observed_delta.index, dataset.observed_delta.columns]
    predicted_post = dataset.control_expression + predicted_delta
    metrics = {
        "mae_delta": mean_absolute_error(
            dataset.observed_delta.to_numpy(), predicted_delta.to_numpy()
        ),
        "mse_delta": mean_squared_error(
            dataset.observed_delta.to_numpy(), predicted_delta.to_numpy()
        ),
        "pearson_delta": pearson_delta_correlation(
            dataset.control_expression.to_numpy(),
            dataset.observed_post_expression.to_numpy(),
            predicted_post.to_numpy(),
        ),
        "spearman_logfc": spearman_logfc_correlation(
            dataset.control_expression.to_numpy(),
            dataset.observed_post_expression.to_numpy(),
            predicted_post.to_numpy(),
        ),
    }
    return {key: _json_safe_float(value) for key, value in metrics.items()}


def evaluate_by_group(
    dataset: DeltaDataset,
    predicted_delta: pd.DataFrame,
    *,
    group_columns: Iterable[str],
) -> pd.DataFrame:
    """Compute metrics by metadata group where each group has at least two values."""
    rows: list[dict[str, object]] = []
    for column in group_columns:
        if column not in dataset.metadata.columns:
            continue
        for value, group_index in dataset.metadata.groupby(column, dropna=False).groups.items():
            subset = subset_delta_dataset(dataset, group_index)
            metrics = evaluate_delta_predictions(subset, predicted_delta.loc[group_index])
            rows.append({"group_column": column, "group_value": value, **metrics})
    return pd.DataFrame(rows)


def subset_delta_dataset(dataset: DeltaDataset, indexer) -> DeltaDataset:
    """Return a DeltaDataset subset by labels, boolean mask, or positional mask."""
    metadata = dataset.metadata.loc[indexer] if not _is_bool_mask(indexer) else dataset.metadata.loc[indexer]
    index = metadata.index
    return DeltaDataset(
        group_ids=tuple(map(str, index)),
        metadata=dataset.metadata.loc[index],
        control_expression=dataset.control_expression.loc[index],
        observed_post_expression=dataset.observed_post_expression.loc[index],
        observed_delta=dataset.observed_delta.loc[index],
    )


def prediction_long_frame(
    dataset: DeltaDataset,
    predicted_delta: pd.DataFrame,
    *,
    baseline: str,
    split_mode: str,
    split_label: str,
) -> pd.DataFrame:
    """Serialize observed/predicted delta and post-expression as a long table."""
    predicted_delta = predicted_delta.loc[dataset.observed_delta.index, dataset.observed_delta.columns]
    predicted_post = dataset.control_expression + predicted_delta
    rows: list[dict[str, object]] = []
    for group_id in dataset.group_ids:
        metadata = dataset.metadata.loc[group_id].to_dict()
        for gene in dataset.gene_names:
            rows.append(
                {
                    "split_mode": split_mode,
                    "split": split_label,
                    "baseline": baseline,
                    "group_id": group_id,
                    "gene": gene,
                    "observed_delta": dataset.observed_delta.loc[group_id, gene],
                    "predicted_delta": predicted_delta.loc[group_id, gene],
                    "observed_post": dataset.observed_post_expression.loc[group_id, gene],
                    "predicted_post": predicted_post.loc[group_id, gene],
                    **metadata,
                }
            )
    return pd.DataFrame(rows)


def _json_safe_float(value: float) -> float | None:
    value = float(value)
    if math.isnan(value) or math.isinf(value):
        return None
    return value


def _is_bool_mask(indexer) -> bool:
    if isinstance(indexer, pd.Series):
        return indexer.dtype == bool
    return False

