"""Conservative preprocessing helpers for real-data smoke benchmarks."""

from __future__ import annotations

from typing import Any

import numpy as np
from anndata import AnnData
from scipy import sparse


def preprocess_adata(adata: AnnData, config: dict[str, Any]) -> AnnData:
    """Apply conservative, config-driven preprocessing for v0.3."""
    preprocessing = config.get("preprocessing", {})
    result = adata.copy()
    result = _downsample_cells(result, preprocessing)
    result = _filter_genes_by_cells(result, preprocessing)
    result = _select_top_variable_genes(result, preprocessing)
    return result


def _downsample_cells(adata: AnnData, preprocessing: dict[str, Any]) -> AnnData:
    max_cells = preprocessing.get("max_cells")
    if max_cells is None or adata.n_obs <= int(max_cells):
        return adata
    seed = int(preprocessing.get("seed", 0))
    rng = np.random.default_rng(seed)
    positions = np.sort(rng.choice(np.arange(adata.n_obs), size=int(max_cells), replace=False))
    return adata[positions].copy()


def _filter_genes_by_cells(adata: AnnData, preprocessing: dict[str, Any]) -> AnnData:
    min_cells = preprocessing.get("min_cells_per_gene")
    if min_cells is None:
        return adata
    min_cells = int(min_cells)
    x = adata.X
    if sparse.issparse(x):
        n_cells = np.asarray((x > 0).sum(axis=0)).ravel()
    else:
        n_cells = (np.asarray(x) > 0).sum(axis=0)
    keep = n_cells >= min_cells
    if not keep.any():
        raise ValueError("gene filtering removed all genes")
    return adata[:, keep].copy()


def _select_top_variable_genes(adata: AnnData, preprocessing: dict[str, Any]) -> AnnData:
    max_genes = preprocessing.get("max_genes")
    if max_genes is None or adata.n_vars <= int(max_genes):
        return adata
    max_genes = int(max_genes)
    x = adata.X
    if sparse.issparse(x):
        mean = np.asarray(x.mean(axis=0)).ravel()
        mean_sq = np.asarray(x.multiply(x).mean(axis=0)).ravel()
        variance = mean_sq - np.square(mean)
    else:
        variance = np.asarray(x, dtype=float).var(axis=0)
    top = np.argsort(-variance, kind="mergesort")[:max_genes]
    top = np.sort(top)
    return adata[:, top].copy()

