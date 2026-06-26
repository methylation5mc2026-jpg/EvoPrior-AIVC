"""Locked metric primitives for perturbation response prediction."""

from __future__ import annotations

import numpy as np


def mean_absolute_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Return elementwise mean absolute error."""
    y_true, y_pred = _paired_arrays(y_true, y_pred)
    return float(np.mean(np.abs(y_true - y_pred)))


def mean_squared_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Return elementwise mean squared error."""
    y_true, y_pred = _paired_arrays(y_true, y_pred)
    return float(np.mean(np.square(y_true - y_pred)))


def pearson_delta_correlation(
    control_expression: np.ndarray,
    observed_post_expression: np.ndarray,
    predicted_post_expression: np.ndarray,
) -> float:
    """Pearson correlation between observed and predicted perturbation deltas."""
    control_expression, observed_post_expression = _paired_arrays(
        control_expression, observed_post_expression
    )
    control_expression, predicted_post_expression = _paired_arrays(
        control_expression, predicted_post_expression
    )
    observed_delta = observed_post_expression - control_expression
    predicted_delta = predicted_post_expression - control_expression
    return _pearson(observed_delta.ravel(), predicted_delta.ravel())


def spearman_logfc_correlation(
    control_expression: np.ndarray,
    observed_post_expression: np.ndarray,
    predicted_post_expression: np.ndarray,
) -> float:
    """Spearman correlation between observed and predicted log1p fold-change.

    Linear baselines can produce negative reconstructed expression values.
    For log-space ranking, expression values are clipped at zero before log1p.
    """
    control_expression, observed_post_expression = _paired_arrays(
        control_expression, observed_post_expression
    )
    control_expression, predicted_post_expression = _paired_arrays(
        control_expression, predicted_post_expression
    )
    control_log = np.log1p(np.clip(control_expression, a_min=0.0, a_max=None))
    observed_logfc = np.log1p(np.clip(observed_post_expression, a_min=0.0, a_max=None))
    observed_logfc = observed_logfc - control_log
    predicted_logfc = np.log1p(np.clip(predicted_post_expression, a_min=0.0, a_max=None))
    predicted_logfc = predicted_logfc - control_log
    return _pearson(
        _rankdata_average(observed_logfc.ravel()),
        _rankdata_average(predicted_logfc.ravel()),
    )


def top_k_de_overlap_precision(
    observed_delta: np.ndarray,
    predicted_delta: np.ndarray,
    *,
    k: int,
    use_absolute: bool = True,
) -> float:
    """Precision@k for overlap of top differential-expression genes."""
    observed_delta, predicted_delta = _paired_arrays(observed_delta, predicted_delta)
    observed_flat = observed_delta.ravel()
    predicted_flat = predicted_delta.ravel()
    if k <= 0:
        raise ValueError("k must be positive")
    if k > observed_flat.size:
        raise ValueError("k must be less than or equal to the number of scores")

    if use_absolute:
        observed_flat = np.abs(observed_flat)
        predicted_flat = np.abs(predicted_flat)

    observed_top = set(_top_k_indices(observed_flat, k))
    predicted_top = set(_top_k_indices(predicted_flat, k))
    return len(observed_top.intersection(predicted_top)) / float(k)


def _paired_arrays(a: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.shape != b.shape:
        raise ValueError(f"shape mismatch: {a.shape} != {b.shape}")
    if not np.all(np.isfinite(a)) or not np.all(np.isfinite(b)):
        raise ValueError("metric inputs must be finite")
    return a, b


def _pearson(a: np.ndarray, b: np.ndarray) -> float:
    a, b = _paired_arrays(a, b)
    a_centered = a - np.mean(a)
    b_centered = b - np.mean(b)
    denominator = np.linalg.norm(a_centered) * np.linalg.norm(b_centered)
    if denominator == 0.0:
        return float("nan")
    return float(np.dot(a_centered, b_centered) / denominator)


def _rankdata_average(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(values.size, dtype=float)
    sorted_values = values[order]

    start = 0
    while start < values.size:
        end = start + 1
        while end < values.size and sorted_values[end] == sorted_values[start]:
            end += 1
        average_rank = (start + end - 1) / 2.0 + 1.0
        ranks[order[start:end]] = average_rank
        start = end

    return ranks


def _top_k_indices(scores: np.ndarray, k: int) -> np.ndarray:
    sorted_indices = np.argsort(-scores, kind="mergesort")
    return sorted_indices[:k]
