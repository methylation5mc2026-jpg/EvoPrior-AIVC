"""Perturbation retrieval / discrimination metrics."""

from __future__ import annotations

import numpy as np
import pandas as pd


def perturbation_retrieval_metrics(
    predicted_delta: pd.DataFrame,
    metadata: pd.DataFrame,
    candidate_profiles: pd.DataFrame,
    *,
    perturbation_column: str = "perturbation",
    similarity: str = "cosine",
) -> pd.DataFrame:
    """Rank candidate perturbation profiles for each predicted delta row."""
    if candidate_profiles.shape[0] < 2:
        return pd.DataFrame(
            [
                {
                    "group_id": group_id,
                    "true_perturbation": metadata.loc[group_id, perturbation_column],
                    "rank": None,
                    "reciprocal_rank": None,
                    "top1_correct": None,
                    "meaningful": False,
                    "reason": "fewer than two candidate perturbations",
                }
                for group_id in predicted_delta.index
            ]
        )
    if similarity != "cosine":
        raise ValueError("only cosine similarity is currently supported")

    candidate_matrix = candidate_profiles.to_numpy(dtype=float)
    rows: list[dict[str, object]] = []
    for group_id, prediction in predicted_delta.iterrows():
        true_perturbation = metadata.loc[group_id, perturbation_column]
        similarities = _cosine_scores(prediction.to_numpy(dtype=float), candidate_matrix)
        ranking = np.argsort(-similarities, kind="mergesort")
        candidate_names = list(candidate_profiles.index)
        ranked_names = [candidate_names[idx] for idx in ranking]
        if true_perturbation not in candidate_profiles.index:
            rows.append(
                {
                    "group_id": group_id,
                    "true_perturbation": true_perturbation,
                    "rank": None,
                    "reciprocal_rank": None,
                    "top1_correct": None,
                    "meaningful": False,
                    "reason": "true perturbation absent from candidates",
                }
            )
            continue
        rank = ranked_names.index(true_perturbation) + 1
        rows.append(
            {
                "group_id": group_id,
                "true_perturbation": true_perturbation,
                "rank": rank,
                "reciprocal_rank": 1.0 / rank,
                "top1_correct": rank == 1,
                "meaningful": True,
                "reason": "",
            }
        )
    return pd.DataFrame(rows)


def summarize_retrieval(retrieval_rows: pd.DataFrame) -> dict[str, float | int | bool | None]:
    """Summarize retrieval rows as top-1 accuracy and MRR."""
    meaningful = retrieval_rows[retrieval_rows["meaningful"] == True]  # noqa: E712
    n = int(meaningful.shape[0])
    if n == 0:
        return {"n": 0, "top1_accuracy": None, "mean_reciprocal_rank": None, "underpowered": True}
    return {
        "n": n,
        "top1_accuracy": float(meaningful["top1_correct"].mean()),
        "mean_reciprocal_rank": float(meaningful["reciprocal_rank"].mean()),
        "underpowered": n < 3,
    }


def candidate_profiles_from_observed(
    observed_delta: pd.DataFrame,
    metadata: pd.DataFrame,
    *,
    perturbation_column: str = "perturbation",
) -> pd.DataFrame:
    """Build candidate perturbation centroids from observed delta rows."""
    return observed_delta.groupby(metadata[perturbation_column]).mean()


def _cosine_scores(vector: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    vector_norm = np.linalg.norm(vector)
    matrix_norm = np.linalg.norm(matrix, axis=1)
    denominator = matrix_norm * vector_norm
    scores = np.zeros(matrix.shape[0], dtype=float)
    valid = denominator > 0
    scores[valid] = matrix[valid] @ vector / denominator[valid]
    return scores

