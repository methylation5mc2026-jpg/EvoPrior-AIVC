import numpy as np
import pytest

from evoprior_aivc.data.pseudobulk import aggregate_pseudobulk
from evoprior_aivc.data.synthetic import make_synthetic_perturbation_adata


def test_pseudobulk_returns_expected_number_of_groups():
    adata = make_synthetic_perturbation_adata(seed=1, cells_per_group=4)

    expression, metadata = aggregate_pseudobulk(adata)

    assert expression.shape == (3 * 4 * 2, 20)
    assert metadata.shape[0] == expression.shape[0]
    assert set(metadata["n_cells"]) == {4}


def test_pseudobulk_mean_matches_manual_group_mean():
    adata = make_synthetic_perturbation_adata(seed=2, cells_per_group=5)

    expression, _ = aggregate_pseudobulk(adata)
    group_id = "cell_type=b_cell|perturbation=pert_a|donor=donor_1"
    mask = (
        (adata.obs["cell_type"] == "b_cell")
        & (adata.obs["perturbation"] == "pert_a")
        & (adata.obs["donor"] == "donor_1")
    )
    manual_mean = np.asarray(adata[mask].X).mean(axis=0)

    np.testing.assert_allclose(expression.loc[group_id].to_numpy(), manual_mean)


def test_pseudobulk_sparse_and_dense_outputs_match():
    dense = make_synthetic_perturbation_adata(seed=3, cells_per_group=4, sparse_x=False)
    sparse = make_synthetic_perturbation_adata(seed=3, cells_per_group=4, sparse_x=True)

    dense_expression, dense_metadata = aggregate_pseudobulk(dense)
    sparse_expression, sparse_metadata = aggregate_pseudobulk(sparse)

    assert dense_metadata.equals(sparse_metadata)
    np.testing.assert_allclose(dense_expression.to_numpy(), sparse_expression.to_numpy())


def test_pseudobulk_filters_groups_below_min_cells():
    adata = make_synthetic_perturbation_adata(seed=4, cells_per_group=3)

    expression, metadata = aggregate_pseudobulk(adata, min_cells=4)

    assert expression.empty
    assert metadata.empty


def test_pseudobulk_rejects_missing_groupby_column():
    adata = make_synthetic_perturbation_adata(seed=5)

    with pytest.raises(KeyError, match="missing"):
        aggregate_pseudobulk(adata, groupby=("cell_type", "missing_column"))
