"""Feature helpers for gene-prior tables."""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd

from evoprior_aivc.priors.gene_prior_table import GenePriorTable


def gene_prior_feature_frame(
    prior_table: GenePriorTable,
    genes: Sequence[str],
    *,
    id_column: str = "gene_symbol",
    impute_strategy: str = "median",
    standardize: bool = True,
    add_missing_indicators: bool = True,
) -> pd.DataFrame:
    """Return a deterministic gene-prior feature matrix for requested genes."""
    return prior_table.feature_matrix(
        genes,
        id_column=id_column,
        impute_strategy=impute_strategy,  # type: ignore[arg-type]
        standardize=standardize,
        add_missing_indicators=add_missing_indicators,
    )
