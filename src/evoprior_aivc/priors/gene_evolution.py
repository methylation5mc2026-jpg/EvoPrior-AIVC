"""Gene evolutionary/conservation prior utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd


def gene_conservation_kernel(
    features: pd.DataFrame | np.ndarray,
    *,
    bandwidth: float = 1.0,
) -> pd.DataFrame | np.ndarray:
    """Return an RBF-style gene relatedness kernel from feature vectors."""
    if bandwidth <= 0:
        raise ValueError("bandwidth must be positive")
    if isinstance(features, pd.DataFrame):
        values = features.to_numpy(dtype=float)
        kernel = _rbf(values, bandwidth=bandwidth)
        return pd.DataFrame(kernel, index=features.index, columns=features.index)
    return _rbf(np.asarray(features, dtype=float), bandwidth=bandwidth)


def _rbf(values: np.ndarray, *, bandwidth: float) -> np.ndarray:
    diff = values[:, None, :] - values[None, :, :]
    distances_sq = np.sum(np.square(diff), axis=2)
    return np.exp(-distances_sq / (2.0 * bandwidth * bandwidth))
