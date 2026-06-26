import pandas as pd
import pytest

from evoprior_aivc.evaluation.perturbation_metrics import (
    candidate_profiles_from_observed,
    perturbation_retrieval_metrics,
    summarize_retrieval,
)


def test_perturbation_retrieval_ranks_correct_candidate_first():
    predicted = pd.DataFrame([[1.0, 0.0], [0.0, 2.0]], index=["g1", "g2"])
    metadata = pd.DataFrame({"perturbation": ["a", "b"]}, index=["g1", "g2"])
    candidates = pd.DataFrame([[1.0, 0.0], [0.0, 1.0]], index=["a", "b"])

    rows = perturbation_retrieval_metrics(predicted, metadata, candidates)
    summary = summarize_retrieval(rows)

    assert rows["rank"].tolist() == [1, 1]
    assert summary["top1_accuracy"] == pytest.approx(1.0)
    assert summary["mean_reciprocal_rank"] == pytest.approx(1.0)


def test_perturbation_retrieval_marks_single_candidate_meaningless():
    predicted = pd.DataFrame([[1.0, 0.0]], index=["g1"])
    metadata = pd.DataFrame({"perturbation": ["a"]}, index=["g1"])
    candidates = pd.DataFrame([[1.0, 0.0]], index=["a"])

    rows = perturbation_retrieval_metrics(predicted, metadata, candidates)

    assert bool(rows.iloc[0]["meaningful"]) is False


def test_candidate_profiles_from_observed_averages_by_perturbation():
    observed = pd.DataFrame([[1.0, 0.0], [3.0, 0.0], [0.0, 2.0]], index=["g1", "g2", "g3"])
    metadata = pd.DataFrame({"perturbation": ["a", "a", "b"]}, index=observed.index)

    profiles = candidate_profiles_from_observed(observed, metadata)

    assert profiles.loc["a", 0] == pytest.approx(2.0)

