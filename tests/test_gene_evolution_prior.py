import numpy as np
import pandas as pd

from evoprior_aivc.priors.gene_evolution import gene_conservation_kernel
from evoprior_aivc.priors.gene_features import gene_prior_feature_frame
from evoprior_aivc.priors.gene_prior_table import GenePriorTable


def test_gene_conservation_kernel_is_symmetric():
    features = pd.DataFrame([[0.0], [1.0]], index=["A", "B"], columns=["x"])

    kernel = gene_conservation_kernel(features, bandwidth=1.0)

    assert np.allclose(kernel.to_numpy(), kernel.to_numpy().T)
    assert np.allclose(np.diag(kernel), 1.0)
    assert kernel.loc["A", "B"] < 1.0


def test_gene_prior_feature_frame_wraps_table_feature_matrix():
    table = GenePriorTable.from_dataframe(
        pd.DataFrame(
            {
                "gene_symbol": ["A", "B"],
                "conservation_score": [0.2, 0.8],
                "is_immune_related": [0, 1],
            }
        )
    )

    features = gene_prior_feature_frame(table, ["A", "B", "C"])

    assert features.shape[0] == 3
    assert features.loc["C", "_prior_missing"] == 1.0
