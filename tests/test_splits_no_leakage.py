import pandas as pd
import pytest

from evoprior_aivc.data.splits import (
    assert_holdout_values_absent,
    assert_no_forbidden_feature_columns,
    assign_group_holdout_split,
    assign_random_group_split,
)


def test_heldout_perturbation_is_absent_from_train_and_val():
    metadata = pd.DataFrame(
        {
            "perturbation": ["control", "A", "B", "control", "A", "B", "control", "A"],
            "cell_type": ["T", "T", "T", "B", "B", "B", "NK", "NK"],
            "donor": ["D1", "D1", "D1", "D2", "D2", "D2", "D3", "D3"],
        }
    )

    split = assign_group_holdout_split(
        metadata,
        {"perturbation": ["B"]},
        val_fraction=0.25,
        seed=11,
    )

    assert set(split[metadata["perturbation"] == "B"]) == {"test"}
    assert_holdout_values_absent(metadata, split, column="perturbation", values=["B"])


def test_heldout_donor_is_absent_from_train_and_val():
    metadata = pd.DataFrame(
        {
            "perturbation": ["control", "A", "B"] * 4,
            "cell_type": ["T", "T", "T", "B", "B", "B", "NK", "NK", "NK", "Mono", "Mono", "Mono"],
            "donor": ["D1"] * 3 + ["D2"] * 3 + ["D3"] * 3 + ["D4"] * 3,
        }
    )

    split = assign_group_holdout_split(
        metadata,
        {"donor": ["D4"]},
        val_fraction=0.25,
        seed=7,
    )

    assert set(split[metadata["donor"] == "D4"]) == {"test"}
    assert_holdout_values_absent(metadata, split, column="donor", values=["D4"])


def test_feature_leakage_check_rejects_post_perturbation_columns():
    with pytest.raises(ValueError, match="forbidden target-derived"):
        assert_no_forbidden_feature_columns(
            ["control_expression", "cell_type_embedding", "post_perturbation_expression"],
            forbidden_columns=["post_perturbation_expression", "target_delta"],
        )


def test_random_group_split_assigns_expected_labels_deterministically():
    metadata = pd.DataFrame({"group": [f"g{i}" for i in range(10)]})

    split_a = assign_random_group_split(metadata, val_fraction=0.2, test_fraction=0.2, seed=123)
    split_b = assign_random_group_split(metadata, val_fraction=0.2, test_fraction=0.2, seed=123)

    assert split_a.equals(split_b)
    assert split_a.value_counts().to_dict() == {"train": 6, "test": 2, "val": 2}


def test_split_requires_existing_holdout_column():
    metadata = pd.DataFrame({"perturbation": ["control", "A"]})

    with pytest.raises(KeyError, match="missing"):
        assign_group_holdout_split(metadata, {"donor": ["D1"]})
