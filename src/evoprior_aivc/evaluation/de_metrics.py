"""Differential-expression recovery metrics over delta vectors."""

from __future__ import annotations

import numpy as np

from evoprior_aivc.evaluation.metrics import _rankdata_average


def de_recovery_metrics(
    observed_delta: np.ndarray,
    predicted_delta: np.ndarray,
    *,
    ks: tuple[int, ...] = (20, 50, 100, 200),
) -> dict[str, float | int | None]:
    """Compute top-k DE recovery metrics for one delta vector."""
    observed, predicted = _paired_vectors(observed_delta, predicted_delta)
    result: dict[str, float | int | None] = {
        "spearman_gene_rank": _spearman(observed, predicted),
    }
    for k in ks:
        capped_k = min(int(k), observed.size)
        obs_top = _top_k_indices(np.abs(observed), capped_k)
        pred_top = _top_k_indices(np.abs(predicted), capped_k)
        intersection = set(obs_top).intersection(set(pred_top))
        precision = len(intersection) / float(capped_k)
        jaccard = len(intersection) / float(len(set(obs_top).union(set(pred_top))))
        direction_hits = [
            np.sign(observed[idx]) == np.sign(predicted[idx])
            for idx in intersection
            if np.sign(observed[idx]) != 0
        ]
        result[f"top_{k}_precision"] = precision
        result[f"top_{k}_jaccard"] = jaccard
        result[f"top_{k}_direction_accuracy"] = (
            float(np.mean(direction_hits)) if direction_hits else None
        )
        result[f"top_{k}_effective_k"] = capped_k
    return result


def _paired_vectors(a: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    a = np.asarray(a, dtype=float).ravel()
    b = np.asarray(b, dtype=float).ravel()
    if a.shape != b.shape:
        raise ValueError(f"shape mismatch: {a.shape} != {b.shape}")
    if not np.all(np.isfinite(a)) or not np.all(np.isfinite(b)):
        raise ValueError("DE metric inputs must be finite")
    return a, b


def _spearman(a: np.ndarray, b: np.ndarray) -> float | None:
    if np.std(a) == 0.0 or np.std(b) == 0.0:
        return None
    a_rank = _rankdata_average(a)
    b_rank = _rankdata_average(b)
    a_centered = a_rank - a_rank.mean()
    b_centered = b_rank - b_rank.mean()
    denominator = np.linalg.norm(a_centered) * np.linalg.norm(b_centered)
    return float(np.dot(a_centered, b_centered) / denominator) if denominator else None


def _top_k_indices(scores: np.ndarray, k: int) -> np.ndarray:
    return np.argsort(-scores, kind="mergesort")[:k]

