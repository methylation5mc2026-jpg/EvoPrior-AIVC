"""GEARS-compatible internal metrics for Norman baseline runs."""

from __future__ import annotations

import pandas as pd

from evoprior_aivc.evaluation.de_metrics import de_recovery_metrics
from evoprior_aivc.evaluation.evaluator import evaluate_delta_predictions, subset_delta_dataset


def per_perturbation_metrics(dataset, predicted_delta: pd.DataFrame) -> pd.DataFrame:
    """Compute scalar metrics per perturbation."""
    rows = []
    grouped = dataset.metadata.groupby("perturbation", dropna=False)
    for perturbation, index in grouped.groups.items():
        subset = subset_delta_dataset(dataset, index)
        metrics = evaluate_delta_predictions(subset, predicted_delta.loc[index])
        row = {"perturbation": str(perturbation), "n_examples": len(subset.group_ids)}
        row.update(metrics)
        rows.append(row)
    return pd.DataFrame(rows)


def per_class_metrics(dataset, predicted_delta: pd.DataFrame) -> pd.DataFrame:
    """Compute scalar metrics by perturbation_type and split_class when available."""
    rows = []
    for column in ("perturbation_type", "split_class"):
        if column not in dataset.metadata.columns:
            continue
        for value, index in dataset.metadata.groupby(column, dropna=False).groups.items():
            subset = subset_delta_dataset(dataset, index)
            metrics = evaluate_delta_predictions(subset, predicted_delta.loc[index])
            row = {
                "group_column": column,
                "group_value": str(value),
                "n_examples": len(subset.group_ids),
            }
            row.update(metrics)
            rows.append(row)
    return pd.DataFrame(rows)


def de_rows_for_dataset(
    dataset,
    predicted_delta: pd.DataFrame,
    *,
    ks: tuple[int, ...],
) -> list[dict[str, object]]:
    """Compute per-example DE recovery rows."""
    rows = []
    for group_id in dataset.group_ids:
        row = de_recovery_metrics(
            dataset.observed_delta.loc[group_id].to_numpy(dtype=float),
            predicted_delta.loc[group_id].to_numpy(dtype=float),
            ks=ks,
        )
        row.update(
            {
                "group_id": group_id,
                "perturbation": dataset.metadata.loc[group_id, "perturbation"],
                "perturbation_type": dataset.metadata.loc[group_id, "perturbation_type"],
                "split_class": dataset.metadata.loc[group_id].get("split_class", "unknown"),
            }
        )
        rows.append(row)
    return rows


def summarize_gears_metric_frames(
    per_perturbation: pd.DataFrame,
    per_class: pd.DataFrame,
) -> dict[str, int]:
    """Return compact counts for reporting/tests."""
    return {
        "n_per_perturbation_rows": int(per_perturbation.shape[0]),
        "n_per_class_rows": int(per_class.shape[0]),
    }
