from evoprior_aivc.baselines import build_delta_dataset
from evoprior_aivc.data.pseudobulk import aggregate_pseudobulk
from evoprior_aivc.data.splits import assign_heldout_cell_type_split
from evoprior_aivc.data.synthetic_gene_prior import (
    make_synthetic_gene_prior_adata,
    make_synthetic_gene_prior_table,
    make_synthetic_gene_prior_tree,
)
from evoprior_aivc.data.validate import validate_adata_schema


def test_synthetic_gene_prior_adata_schema_and_prior_alignment():
    adata, prior = make_synthetic_gene_prior_adata(seed=1, cells_per_group=3)
    report = validate_adata_schema(adata)
    features = prior.feature_matrix(list(adata.var["gene_symbol"])[:10])

    assert report.n_obs == adata.n_obs
    assert adata.obs["cell_type"].nunique() >= 6
    assert features.shape[0] == 10


def test_synthetic_gene_prior_modulated_genes_have_stronger_response():
    adata, _ = make_synthetic_gene_prior_adata(seed=2, cells_per_group=4)
    expression, metadata = aggregate_pseudobulk(
        adata,
        groupby=("cell_type", "perturbation", "donor"),
        min_cells=2,
    )
    dataset = build_delta_dataset(
        expression,
        metadata,
        control_label="control",
        match_columns=("cell_type", "donor"),
    )
    stim_a = dataset.metadata["perturbation"] == "stim_a"
    delta = dataset.observed_delta.loc[stim_a]

    immune_block = delta.loc[:, "SGENE030":"SGENE059"].abs().to_numpy().mean()
    missing_block = delta.loc[:, "SGENE105":"SGENE119"].abs().to_numpy().mean()

    assert immune_block > missing_block


def test_synthetic_gene_prior_shuffle_breaks_gene_feature_association():
    prior = make_synthetic_gene_prior_table()
    shuffled = prior.shuffled_control(seed=3)

    original = prior.to_dataframe()["conservation_score"].tolist()
    shuffled_values = shuffled.to_dataframe()["conservation_score"].tolist()

    assert sorted(original, key=lambda value: -1 if value is None else float(value)) != []
    assert original != shuffled_values


def test_synthetic_gene_prior_pseudobulk_and_split_work():
    adata, _ = make_synthetic_gene_prior_adata(seed=4, cells_per_group=3)
    tree = make_synthetic_gene_prior_tree()
    expression, metadata = aggregate_pseudobulk(
        adata,
        groupby=("cell_type", "perturbation", "donor"),
        min_cells=2,
    )
    dataset = build_delta_dataset(
        expression,
        metadata,
        control_label="control",
        match_columns=("cell_type", "donor"),
    )
    split = assign_heldout_cell_type_split(dataset.metadata, heldout_cell_type="cd8_like")

    assert tree.tree_distance("cd4_like", "cd8_like") < tree.tree_distance("cd4_like", "mono_like")
    assert (split == "test").any()
    assert (split == "train").any()
