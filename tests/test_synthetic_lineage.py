import numpy as np

from evoprior_aivc.data.pseudobulk import aggregate_pseudobulk
from evoprior_aivc.data.synthetic_lineage import (
    CELL_TYPES,
    PERTURBATIONS,
    heldout_cell_type_split,
    make_synthetic_lineage_adata,
    make_synthetic_lineage_tree,
)
from evoprior_aivc.data.validate import validate_adata_schema


def test_synthetic_lineage_adata_schema_and_group_content():
    adata = make_synthetic_lineage_adata(seed=1, cells_per_group=4)

    report = validate_adata_schema(adata)

    assert report.n_vars == 40
    assert set(CELL_TYPES).issubset(set(adata.obs["cell_type"]))
    assert set(PERTURBATIONS).issubset(set(adata.obs["perturbation"]))
    assert int(adata.obs["is_control"].sum()) > 0


def test_synthetic_lineage_pseudobulk_and_heldout_split():
    adata = make_synthetic_lineage_adata(seed=2, cells_per_group=4)
    expression, metadata = aggregate_pseudobulk(adata)

    split = heldout_cell_type_split(metadata, heldout_cell_type="myeloid_b")

    assert expression.shape[0] == len(CELL_TYPES) * len(PERTURBATIONS) * 2
    assert set(split[metadata["cell_type"] == "myeloid_b"]) == {"test"}
    assert "myeloid_b" not in set(metadata.loc[split == "train", "cell_type"])


def test_known_sibling_lineage_pattern_is_present():
    adata = make_synthetic_lineage_adata(seed=3, cells_per_group=8)
    expression, metadata = aggregate_pseudobulk(adata)
    stim = "stim_a"

    def delta(cell_type):
        post_mask = (metadata["cell_type"] == cell_type) & (metadata["perturbation"] == stim)
        ctrl_mask = (metadata["cell_type"] == cell_type) & (metadata["perturbation"] == "control")
        return expression.loc[post_mask].mean(axis=0) - expression.loc[ctrl_mask].mean(axis=0)

    myeloid_a = delta("myeloid_a").to_numpy()
    myeloid_b = delta("myeloid_b").to_numpy()
    epithelial_a = delta("epithelial_a").to_numpy()

    sibling_distance = np.linalg.norm(myeloid_a - myeloid_b)
    unrelated_distance = np.linalg.norm(myeloid_a - epithelial_a)
    assert sibling_distance < unrelated_distance


def test_synthetic_lineage_tree_matches_expected_distances():
    tree = make_synthetic_lineage_tree()

    assert tree.tree_distance("myeloid_a", "myeloid_b") == 2
    assert tree.tree_distance("myeloid_a", "epithelial_a") > 2
