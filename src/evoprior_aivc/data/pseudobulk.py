"""Pseudobulk aggregation utilities."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd
from anndata import AnnData
from scipy import sparse


def aggregate_pseudobulk(
    adata: AnnData,
    groupby: Sequence[str] = ("cell_type", "perturbation", "donor"),
    *,
    layer: str | None = None,
    min_cells: int = 1,
    aggregation: str = "mean",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Aggregate single-cell expression into pseudobulk profiles.

    Returns ``(expression, metadata)`` DataFrames with matching indexes. The
    expression table is group-by-gene, and metadata preserves group columns plus
    ``n_cells``.
    """
    if not isinstance(adata, AnnData):
        raise TypeError("adata must be an anndata.AnnData object")
    if not groupby:
        raise ValueError("groupby must contain at least one obs column")
    if min_cells < 1:
        raise ValueError("min_cells must be at least 1")
    if aggregation != "mean":
        raise ValueError("only aggregation='mean' is currently supported")

    missing = [column for column in groupby if column not in adata.obs.columns]
    if missing:
        missing_list = ", ".join(missing)
        raise KeyError(f"groupby columns are missing from adata.obs: {missing_list}")

    x = adata.layers[layer] if layer is not None else adata.X
    gene_names = _gene_names(adata)
    metadata = adata.obs.loc[:, list(groupby)].copy()

    expression_rows: list[np.ndarray] = []
    metadata_rows: list[dict[str, object]] = []
    index: list[str] = []

    grouped = metadata.groupby(list(groupby), sort=True, dropna=False, observed=True)
    for group_key, positions in grouped.indices.items():
        if not isinstance(group_key, tuple):
            group_key = (group_key,)
        n_cells = len(positions)
        if n_cells < min_cells:
            continue

        expression_rows.append(_mean_rows(x, positions))
        row = {column: value for column, value in zip(groupby, group_key, strict=True)}
        row["n_cells"] = n_cells
        metadata_rows.append(row)
        index.append(_group_id(groupby, group_key))

    expression = pd.DataFrame(expression_rows, index=index, columns=gene_names, dtype=float)
    grouped_metadata = pd.DataFrame(metadata_rows, index=index)
    return expression, grouped_metadata


def _mean_rows(x, positions: np.ndarray) -> np.ndarray:
    selected = x[positions]
    if sparse.issparse(selected):
        return np.asarray(selected.mean(axis=0)).ravel()
    return np.asarray(selected, dtype=float).mean(axis=0).ravel()


def _gene_names(adata: AnnData) -> list[str]:
    if "gene_symbol" in adata.var.columns:
        return list(map(str, adata.var["gene_symbol"]))
    if "gene_id" in adata.var.columns:
        return list(map(str, adata.var["gene_id"]))
    return list(map(str, adata.var_names))


def _group_id(groupby: Sequence[str], group_key: tuple[object, ...]) -> str:
    return "|".join(f"{column}={value}" for column, value in zip(groupby, group_key, strict=True))
