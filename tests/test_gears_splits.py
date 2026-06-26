import pandas as pd

from evoprior_aivc.data.gears_splits import assign_gears_compatible_combo_split


def test_assign_gears_compatible_combo_split_has_no_test_combo_leakage():
    metadata = pd.DataFrame(
        {
            "perturbation": [
                "A",
                "B",
                "C",
                "D",
                "A+B",
                "A+C",
                "C+D",
                "B+D",
            ],
            "perturbation_type": [
                "single",
                "single",
                "single",
                "single",
                "combo",
                "combo",
                "combo",
                "combo",
            ],
            "perturbation_genes": [
                "A",
                "B",
                "C",
                "D",
                "A;B",
                "A;C",
                "C;D",
                "B;D",
            ],
        },
        index=[f"g{i}" for i in range(8)],
    )

    split, manifest, audit = assign_gears_compatible_combo_split(
        metadata,
        seed=1,
        seen_gene_fraction=0.5,
        test_combo_fraction=0.5,
        val_fraction=0.0,
    )

    assert set(split.astype(str)).issubset({"train", "test"})
    assert audit["overall_pass"] is True
    assert audit["n_test_combos"] >= 1
    assert "split_class" in manifest.columns


def test_assign_gears_split_can_label_random_combo_holdouts():
    metadata = pd.DataFrame(
        {
            "perturbation": ["A", "B", "C", "D", "A+B", "A+C", "C+D", "B+D"],
            "perturbation_type": [
                "single",
                "single",
                "single",
                "single",
                "combo",
                "combo",
                "combo",
                "combo",
            ],
            "perturbation_genes": ["A", "B", "C", "D", "A;B", "A;C", "C;D", "B;D"],
        },
        index=[f"g{i}" for i in range(8)],
    )

    _, manifest, audit = assign_gears_compatible_combo_split(
        metadata,
        seed=1,
        seen_gene_fraction=1.0,
        test_combo_fraction=0.0,
        random_combo_fraction=0.5,
        val_fraction=0.0,
    )

    assert "random_combo" in set(manifest["split_class"])
    assert "random_combo" in audit["split_category_values"]
