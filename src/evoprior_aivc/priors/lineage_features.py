"""Feature utilities derived from cell-lineage trees."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

import numpy as np
import pandas as pd

from evoprior_aivc.priors.cell_lineage import CellTypeLineageMapper, LineageTree


def pairwise_distance_matrix(
    tree: LineageTree,
    cell_types: Sequence[str],
    *,
    mapper: CellTypeLineageMapper | None = None,
) -> pd.DataFrame:
    """Return a pairwise tree-distance matrix for cell types or lineage nodes."""
    nodes = _to_nodes(cell_types, mapper)
    matrix = np.zeros((len(nodes), len(nodes)), dtype=float)
    for i, a in enumerate(nodes):
        for j, b in enumerate(nodes):
            matrix[i, j] = tree.tree_distance(a, b)
    return pd.DataFrame(matrix, index=list(cell_types), columns=list(cell_types))


def relatedness_kernel(
    distance: np.ndarray | pd.DataFrame,
    *,
    tau: float = 1.0,
) -> np.ndarray | pd.DataFrame:
    """Convert distances to exp(-distance / tau) relatedness values."""
    if tau <= 0:
        raise ValueError("tau must be positive")
    if isinstance(distance, pd.DataFrame):
        values = np.exp(-distance.to_numpy(dtype=float) / tau)
        return pd.DataFrame(values, index=distance.index, columns=distance.columns)
    return np.exp(-np.asarray(distance, dtype=float) / tau)


def clade_membership_matrix(
    tree: LineageTree,
    cell_types: Sequence[str],
    *,
    ancestor_nodes: Iterable[str],
    mapper: CellTypeLineageMapper | None = None,
) -> pd.DataFrame:
    """Return binary membership of cell types in selected ancestor clades."""
    nodes = _to_nodes(cell_types, mapper)
    ancestors = list(ancestor_nodes)
    rows = []
    for node in nodes:
        node_ancestors = set(tree.ancestors(node, include_self=True))
        rows.append([1.0 if ancestor in node_ancestors else 0.0 for ancestor in ancestors])
    return pd.DataFrame(rows, index=list(cell_types), columns=ancestors, dtype=float)


def lineage_feature_frame(
    tree: LineageTree,
    cell_types: Sequence[str],
    *,
    mapper: CellTypeLineageMapper | None = None,
    clade_nodes: Iterable[str] | None = None,
) -> pd.DataFrame:
    """Return depth plus optional clade membership features."""
    nodes = _to_nodes(cell_types, mapper)
    frame = pd.DataFrame(
        {
            "lineage_node": nodes,
            "lineage_depth": [tree.depth(node) for node in nodes],
        },
        index=list(cell_types),
    )
    if clade_nodes is not None:
        clades = clade_membership_matrix(
            tree,
            cell_types,
            ancestor_nodes=clade_nodes,
            mapper=mapper,
        )
        frame = pd.concat([frame, clades.add_prefix("clade_")], axis=1)
    return frame


def _to_nodes(cell_types: Sequence[str], mapper: CellTypeLineageMapper | None) -> list[str]:
    if mapper is None:
        return list(cell_types)
    return mapper.map_many(cell_types)
