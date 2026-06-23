import pytest

from evoprior_aivc.evaluation.statistics import normal_approx_ci


def test_normal_approx_ci_reports_underpowered_for_single_value():
    summary = normal_approx_ci([1.0])

    assert summary["mean"] == 1.0
    assert summary["ci_low"] is None
    assert summary["underpowered"] is True


def test_normal_approx_ci_computes_interval_for_multiple_values():
    summary = normal_approx_ci([1.0, 2.0, 3.0, 4.0])

    assert summary["n"] == 4
    assert summary["mean"] == pytest.approx(2.5)
    assert summary["ci_low"] < summary["mean"] < summary["ci_high"]

