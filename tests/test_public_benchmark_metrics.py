import pandas as pd

from evoprior_aivc.evaluation.public_benchmark_metrics import (
    split_leakage_audit,
    split_size_table,
)


def test_split_leakage_audit_passes_for_leave_one_perturbation_manifest():
    manifest = pd.DataFrame(
        {
            "group_id": ["g0", "g1", "g2", "g3"],
            "heldout_perturbation": ["p1", "p1", "p1", "p1"],
            "split": ["train", "val", "test", "test"],
            "perturbation": ["p2", "control", "p1", "p1"],
            "n_cells": [20, 30, 25, 25],
        }
    )

    audit = split_leakage_audit(manifest)
    sizes = split_size_table(manifest)

    assert audit["overall_pass"] is True
    assert audit["rows"][0]["n_test"] == 2
    assert int(sizes.loc[sizes["split"] == "test", "n_cells"].iloc[0]) == 50


def test_split_leakage_audit_fails_when_heldout_appears_in_train():
    manifest = pd.DataFrame(
        {
            "group_id": ["g0", "g1"],
            "heldout_perturbation": ["p1", "p1"],
            "split": ["train", "test"],
            "perturbation": ["p1", "p1"],
        }
    )

    audit = split_leakage_audit(manifest)

    assert audit["overall_pass"] is False
    assert audit["rows"][0]["leaked_perturbations"] == ["p1"]
