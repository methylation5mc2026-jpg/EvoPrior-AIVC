import pandas as pd

from evoprior_aivc.data.splits import assign_group_holdout_split, assign_random_group_split
from evoprior_aivc.evaluation.leakage_checks import assert_holdout_split_has_no_train_leakage


def test_real_style_heldout_perturbation_split_is_group_level_safe():
    metadata = pd.DataFrame(
        {
            "cell_type": ["monocyte"] * 5,
            "perturbation": ["control", "irf1", "stat2", "pdl1", "pdl1"],
            "guide_id": ["nt", "g1", "g2", "g3", "g4"],
        },
        index=[f"group_{idx}" for idx in range(5)],
    )

    split = assign_group_holdout_split(
        metadata,
        holdout={"perturbation": ["pdl1"]},
        val_fraction=0.2,
        seed=3,
    )

    assert set(split[metadata["perturbation"] == "pdl1"]) == {"test"}
    assert_holdout_split_has_no_train_leakage(
        metadata,
        split,
        holdout={"perturbation": ["pdl1"]},
    )


def test_random_group_split_operates_on_metadata_rows_not_cells():
    metadata = pd.DataFrame(
        {"n_cells": [100, 20, 35, 50, 60]},
        index=["pb_1", "pb_2", "pb_3", "pb_4", "pb_5"],
    )

    split = assign_random_group_split(metadata, val_fraction=0.2, test_fraction=0.2, seed=1)

    assert len(split) == metadata.shape[0]
    assert set(split.index) == set(metadata.index)

