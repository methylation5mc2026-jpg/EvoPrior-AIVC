import pandas as pd
import pytest

from evoprior_aivc.priors.gene_prior_table import GenePriorTable


def test_gene_prior_table_detects_duplicate_symbols():
    frame = pd.DataFrame({"gene_symbol": ["A", "A"], "conservation_score": [0.1, 0.2]})

    with pytest.raises(ValueError, match="duplicate gene_symbol"):
        GenePriorTable.from_dataframe(frame)


def test_gene_prior_table_feature_matrix_handles_unknowns_and_missing():
    table = GenePriorTable.from_dataframe(
        pd.DataFrame(
            {
                "gene_symbol": ["A", "B"],
                "conservation_score": [1.0, None],
                "ortholog_count": [10, 3],
                "is_housekeeping": [1, 0],
                "go_slim_category": ["core", None],
                "source": ["toy", "toy"],
                "source_version": ["v1", "v1"],
            }
        )
    )

    features = table.feature_matrix(["A", "B", "C"])

    assert features.shape[0] == 3
    assert "_prior_missing" in features.columns
    assert features.loc["C", "_prior_missing"] == 1.0
    assert any(column.startswith("missing_") for column in features.columns)


def test_gene_prior_table_coverage_and_shuffle_are_deterministic():
    frame = pd.DataFrame(
        {
            "gene_symbol": ["A", "B", "C"],
            "conservation_score": [0.1, 0.5, 0.9],
            "ortholog_count": [1, 2, 3],
            "source": ["toy", "toy", "toy"],
            "source_version": ["v1", "v1", "v1"],
        }
    )
    table = GenePriorTable.from_dataframe(frame)

    coverage = table.coverage_for_genes(["A", "Z"])
    shuffled_a = table.shuffled_control(seed=7).to_dataframe()
    shuffled_b = table.shuffled_control(seed=7).to_dataframe()

    assert coverage.n_mapped == 1
    assert coverage.missing_genes == ("Z",)
    assert shuffled_a["conservation_score"].tolist() == shuffled_b["conservation_score"].tolist()
    assert sorted(shuffled_a["conservation_score"].tolist()) == [0.1, 0.5, 0.9]


def test_gene_prior_table_validates_numeric_ranges():
    with pytest.raises(ValueError, match="conservation_score"):
        GenePriorTable.from_dataframe(
            pd.DataFrame({"gene_symbol": ["A"], "conservation_score": [1.5]})
        )
