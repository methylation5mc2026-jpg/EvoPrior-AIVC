import pandas as pd
import pytest

from evoprior_aivc.evaluation.leakage_checks import (
    assert_holdout_split_has_no_train_leakage,
    assert_no_target_derived_features,
    assert_required_split_labels,
)


def test_holdout_split_leakage_check_accepts_clean_split():
    metadata = pd.DataFrame({"perturbation": ["pert_a", "pert_b", "pert_c"]})
    split = pd.Series(["train", "val", "test"])

    assert_holdout_split_has_no_train_leakage(
        metadata,
        split,
        holdout={"perturbation": ["pert_c"]},
    )


def test_holdout_split_leakage_check_rejects_leak():
    metadata = pd.DataFrame({"cell_type": ["t_cell", "b_cell", "monocyte"]})
    split = pd.Series(["train", "test", "val"])

    with pytest.raises(ValueError, match="leaked"):
        assert_holdout_split_has_no_train_leakage(
            metadata,
            split,
            holdout={"cell_type": ["monocyte"]},
        )


def test_required_split_labels_are_enforced():
    with pytest.raises(ValueError, match="test"):
        assert_required_split_labels(["train", "train", "val"])


def test_target_derived_feature_names_are_rejected():
    with pytest.raises(ValueError, match="target-derived"):
        assert_no_target_derived_features(["control_expression", "observed_delta_gene_1"])

