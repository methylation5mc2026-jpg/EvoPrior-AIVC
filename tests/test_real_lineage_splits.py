import pandas as pd
import pytest

from evoprior_aivc.data.splits import (
    assign_heldout_cell_type_split,
    assign_heldout_lineage_split,
    heldout_cell_type_eligibility,
)
from evoprior_aivc.evaluation.leakage_checks import (
    assert_no_heldout_cell_type_target_leakage,
)


def test_heldout_cell_type_split_keeps_target_test_only():
    metadata = pd.DataFrame(
        {
            "cell_type": ["t", "t", "b", "b", "mono", "mono"],
            "perturbation": ["stim"] * 6,
        },
        index=[f"g{idx}" for idx in range(6)],
    )

    split = assign_heldout_cell_type_split(metadata, heldout_cell_type="b")

    assert set(split[metadata["cell_type"] == "b"]) == {"test"}
    assert set(split[metadata["cell_type"] != "b"]) == {"train"}
    assert_no_heldout_cell_type_target_leakage(
        metadata,
        split,
        heldout_cell_type="b",
        control_usage="control_observed_ood",
    )


def test_heldout_lineage_split_holds_out_multiple_cell_types():
    metadata = pd.DataFrame(
        {"cell_type": ["t", "b", "mono", "dc"], "perturbation": ["stim"] * 4},
        index=["g1", "g2", "g3", "g4"],
    )

    split = assign_heldout_lineage_split(
        metadata,
        heldout_cell_types=["t", "b"],
    )

    assert set(metadata.loc[split == "test", "cell_type"]) == {"t", "b"}
    assert set(metadata.loc[split == "train", "cell_type"]) == {"mono", "dc"}


def test_heldout_cell_type_eligibility_reports_sparse_failures():
    pseudobulk = pd.DataFrame(
        {
            "cell_type": ["t", "t", "t", "b", "b", "mono", "mono", "mono"],
            "perturbation": ["ctrl", "stim", "stim", "ctrl", "stim", "ctrl", "stim", "stim"],
        }
    )

    eligibility = heldout_cell_type_eligibility(
        pseudobulk,
        control_label="ctrl",
        min_test_groups=2,
    )

    assert eligibility.set_index("cell_type").loc["t", "eligible"].item() is True
    assert eligibility.set_index("cell_type").loc["b", "eligible"].item() is False
    assert "too_few_test_groups" in eligibility.set_index("cell_type").loc["b", "reason"]


def test_heldout_leakage_check_rejects_train_target_leak():
    metadata = pd.DataFrame({"cell_type": ["b", "t"], "perturbation": ["stim", "stim"]})
    split = pd.Series(["train", "train"], index=metadata.index)

    with pytest.raises(ValueError, match="held-out cell_type values leaked"):
        assert_no_heldout_cell_type_target_leakage(
            metadata,
            split,
            heldout_cell_type="b",
            control_usage="control_observed_ood",
        )
