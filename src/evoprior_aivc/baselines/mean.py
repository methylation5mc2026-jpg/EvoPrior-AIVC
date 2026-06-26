"""Mean-delta baseline."""

from __future__ import annotations

from typing import Literal

import numpy as np
import pandas as pd

from evoprior_aivc.baselines.base import DeltaBaseline, DeltaDataset


class MeanDeltaBaseline(DeltaBaseline):
    """Predict the average training delta for each perturbation.

    Unseen perturbations use either the global training mean delta or zero delta,
    controlled by ``fallback``.
    """

    name = "mean_delta"

    def __init__(self, *, fallback: Literal["global", "zero"] = "global") -> None:
        if fallback not in {"global", "zero"}:
            raise ValueError("fallback must be 'global' or 'zero'")
        self.fallback = fallback

    def fit(self, dataset: DeltaDataset) -> "MeanDeltaBaseline":
        self.gene_names_ = dataset.gene_names
        self.global_mean_ = dataset.observed_delta.mean(axis=0)
        self.perturbation_means_ = dataset.observed_delta.groupby(dataset.metadata["perturbation"]).mean()
        return self

    def predict_delta(self, dataset: DeltaDataset) -> pd.DataFrame:
        rows: list[np.ndarray] = []
        for perturbation in dataset.metadata["perturbation"]:
            if perturbation in self.perturbation_means_.index:
                rows.append(self.perturbation_means_.loc[perturbation].to_numpy(dtype=float))
            elif self.fallback == "global":
                rows.append(self.global_mean_.to_numpy(dtype=float))
            else:
                rows.append(np.zeros(len(self.gene_names_), dtype=float))
        return pd.DataFrame(rows, index=dataset.metadata.index, columns=self.gene_names_, dtype=float)

