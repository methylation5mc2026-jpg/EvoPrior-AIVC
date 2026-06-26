import pandas as pd
import pytest

from evoprior_aivc.evaluation.prior_audit import (
    assert_gene_prior_features_do_not_use_response_labels,
    correction_magnitude_summary,
    shuffled_prior_preserves_marginals,
    top_corrected_genes,
)
from evoprior_aivc.priors.gene_prior_table import GenePriorTable


def test_prior_audit_rejects_response_derived_feature_names():
    with pytest.raises(ValueError, match="response-derived"):
        assert_gene_prior_features_do_not_use_response_labels(
            ["conservation_score", "target_delta_mean"]
        )


def test_shuffled_prior_preserves_numeric_marginals():
    table = GenePriorTable.from_dataframe(
        pd.DataFrame(
            {
                "gene_symbol": ["A", "B", "C"],
                "conservation_score": [0.1, 0.5, 0.9],
                "ortholog_count": [1, 2, 3],
            }
        )
    )

    assert shuffled_prior_preserves_marginals(table, table.shuffled_control(seed=1))


def test_correction_magnitude_and_top_genes():
    correction = pd.Series({"A": 0.5, "B": -2.0, "C": 0.1})
    summary = correction_magnitude_summary(correction)
    top = top_corrected_genes(correction, n=2)

    assert summary["max_abs"] == 2.0
    assert top["gene"].tolist() == ["B", "A"]
