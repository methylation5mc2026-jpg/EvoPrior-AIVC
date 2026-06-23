import numpy as np
import pytest

from evoprior_aivc.evaluation.de_metrics import de_recovery_metrics


def test_de_recovery_top_k_overlap_and_direction():
    observed = np.array([5.0, -4.0, 0.5, 0.0])
    predicted = np.array([4.5, 0.1, -3.5, 0.0])

    metrics = de_recovery_metrics(observed, predicted, ks=(2,))

    assert metrics["top_2_precision"] == pytest.approx(0.5)
    assert metrics["top_2_jaccard"] == pytest.approx(1 / 3)
    assert metrics["top_2_direction_accuracy"] == pytest.approx(1.0)
    assert metrics["top_2_effective_k"] == 2


def test_de_recovery_caps_k_to_gene_count():
    metrics = de_recovery_metrics(np.array([1.0, 2.0]), np.array([1.0, 2.0]), ks=(10,))

    assert metrics["top_10_effective_k"] == 2
    assert metrics["top_10_precision"] == pytest.approx(1.0)

