import numpy as np
import pandas as pd
import pytest

from evoprior_aivc.priors.cell_lineage import CellTypeLineageMapper, LineageTree
from evoprior_aivc.priors.lineage_features import (
    clade_membership_matrix,
    lineage_feature_frame,
    pairwise_distance_matrix,
    relatedness_kernel,
)


def _tree():
    return LineageTree.from_edges(
        [
            (None, "root"),
            ("root", "immune"),
            ("immune", "myeloid"),
            ("immune", "lymphoid"),
            ("root", "epithelial"),
            ("epithelial", "epithelial_a"),
            ("myeloid", "myeloid_a"),
            ("myeloid", "myeloid_b"),
            ("lymphoid", "lymphoid_a"),
        ]
    )


def test_lineage_tree_lca_distance_and_validation():
    tree = _tree()
    report = tree.validate()

    assert report.root == "root"
    assert tree.parent("immune") == "root"
    assert tree.children("myeloid") == ("myeloid_a", "myeloid_b")
    assert tree.lowest_common_ancestor("myeloid_a", "myeloid_b") == "myeloid"
    assert tree.lowest_common_ancestor("myeloid_a", "lymphoid_a") == "immune"
    assert tree.tree_distance("myeloid_a", "myeloid_b") == 2
    assert tree.tree_distance("myeloid_a", "epithelial_a") == 5


def test_lineage_tree_rejects_multiple_roots_and_duplicate_children():
    with pytest.raises(ValueError, match="exactly one root"):
        LineageTree.from_edges([(None, "root_a"), (None, "root_b")])

    with pytest.raises(ValueError, match="duplicate"):
        LineageTree.from_edges([(None, "root"), ("root", "a"), ("root", "a")])


def test_lineage_tree_from_dataframe():
    df = pd.DataFrame({"parent": [None, "root"], "child": ["root", "immune"]})
    tree = LineageTree.from_dataframe(df)

    assert tree.root == "root"
    assert tree.parent("immune") == "root"


def test_cell_type_mapper_synonyms_and_unknown_behavior():
    mapper = CellTypeLineageMapper(
        {"cd4_t": "lymphoid_a", "mono": "myeloid_a"},
        synonyms={"CD4 T": "cd4_t"},
        unknown_node="unknown",
        on_unknown="unknown",
    )

    assert mapper.map_one("CD4 T") == "lymphoid_a"
    assert mapper.map_one("mystery") == "unknown"
    assert mapper.unmapped(["CD4 T", "mystery"]) == ["mystery"]

    strict = CellTypeLineageMapper({"mono": "myeloid_a"})
    with pytest.raises(KeyError, match="unmapped"):
        strict.map_one("unknown")


def test_lineage_feature_utilities():
    tree = _tree()
    cell_types = ["myeloid_a", "myeloid_b", "epithelial_a"]

    distances = pairwise_distance_matrix(tree, cell_types)
    kernel = relatedness_kernel(distances, tau=2.0)
    clades = clade_membership_matrix(tree, cell_types, ancestor_nodes=["immune", "myeloid"])
    features = lineage_feature_frame(tree, cell_types, clade_nodes=["immune"])

    assert distances.loc["myeloid_a", "myeloid_b"] == 2.0
    assert distances.loc["myeloid_a", "epithelial_a"] == 5.0
    assert np.allclose(np.diag(kernel.to_numpy()), 1.0)
    assert kernel.loc["myeloid_a", "myeloid_b"] > kernel.loc["myeloid_a", "epithelial_a"]
    assert clades.loc["myeloid_a", "immune"] == 1.0
    assert clades.loc["epithelial_a", "immune"] == 0.0
    assert "lineage_depth" in features.columns
