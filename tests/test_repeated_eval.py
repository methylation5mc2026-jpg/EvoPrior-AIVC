import pandas as pd
import pytest

from evoprior_aivc.evaluation.repeated import perturbations_with_min_groups, repeated_seeds


def test_repeated_seeds_are_deterministic():
    assert repeated_seeds(10, 3) == [10, 11, 12]
    with pytest.raises(ValueError):
        repeated_seeds(10, 0)


def test_perturbations_with_min_groups_returns_skips():
    metadata = pd.DataFrame({"perturbation": ["a", "a", "b", "c", "c", "c"]})

    eligible, skipped = perturbations_with_min_groups(metadata, min_test_groups=2)

    assert eligible == ["a", "c"]
    assert skipped.iloc[0]["perturbation"] == "b"

