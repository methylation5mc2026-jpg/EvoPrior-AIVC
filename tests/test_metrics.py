import math

import numpy as np
import pytest

from evoprior_aivc.evaluation.metrics import (
    mean_absolute_error,
    mean_squared_error,
    pearson_delta_correlation,
    spearman_logfc_correlation,
    top_k_de_overlap_precision,
)


def test_error_metrics_match_hand_calculation():
    y_true = np.array([[1.0, 2.0], [3.0, 4.0]])
    y_pred = np.array([[1.0, 1.0], [5.0, 4.0]])

    assert mean_absolute_error(y_true, y_pred) == pytest.approx(0.75)
    assert mean_squared_error(y_true, y_pred) == pytest.approx(1.25)


def test_delta_correlations_are_perfect_for_identical_predictions():
    control = np.array([1.0, 1.0, 1.0, 1.0])
    observed = np.array([2.0, 3.0, 4.0, 5.0])
    predicted = np.array([2.0, 3.0, 4.0, 5.0])

    assert pearson_delta_correlation(control, observed, predicted) == pytest.approx(1.0)
    assert spearman_logfc_correlation(control, observed, predicted) == pytest.approx(1.0)


def test_top_k_de_overlap_precision_uses_absolute_delta_by_default():
    observed_delta = np.array([10.0, -9.0, 1.0, 0.0])
    predicted_delta = np.array([10.0, 1.0, -9.0, 0.0])

    assert top_k_de_overlap_precision(observed_delta, predicted_delta, k=2) == pytest.approx(0.5)


def test_constant_delta_correlation_returns_nan():
    control = np.array([1.0, 1.0, 1.0])
    observed = np.array([2.0, 2.0, 2.0])
    predicted = np.array([3.0, 3.0, 3.0])

    assert math.isnan(pearson_delta_correlation(control, observed, predicted))


def test_metric_shape_mismatch_raises():
    with pytest.raises(ValueError, match="shape mismatch"):
        mean_absolute_error(np.array([1.0, 2.0]), np.array([[1.0, 2.0]]))
