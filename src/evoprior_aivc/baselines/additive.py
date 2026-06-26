"""Additive perturbation and cell-type baseline."""

from __future__ import annotations

import numpy as np
import pandas as pd

from evoprior_aivc.baselines.base import DeltaBaseline, DeltaDataset


class AdditiveBaseline(DeltaBaseline):
    """Predict delta as global mean plus perturbation and cell-type offsets."""

    name = "additive"

    def fit(self, dataset: DeltaDataset) -> AdditiveBaseline:
        self.gene_names_ = dataset.gene_names
        self.global_mean_ = dataset.observed_delta.mean(axis=0)
        self.perturbation_offsets_ = (
            dataset.observed_delta.groupby(dataset.metadata["perturbation"]).mean()
            - self.global_mean_
        )
        self.cell_type_offsets_ = (
            dataset.observed_delta.groupby(dataset.metadata["cell_type"]).mean() - self.global_mean_
        )
        return self

    def predict_delta(self, dataset: DeltaDataset) -> pd.DataFrame:
        rows: list[np.ndarray] = []
        global_delta = self.global_mean_.to_numpy(dtype=float)
        zero = np.zeros(len(self.gene_names_), dtype=float)
        for _, row in dataset.metadata.iterrows():
            perturb_offset = (
                self.perturbation_offsets_.loc[row["perturbation"]].to_numpy(dtype=float)
                if row["perturbation"] in self.perturbation_offsets_.index
                else zero
            )
            cell_offset = (
                self.cell_type_offsets_.loc[row["cell_type"]].to_numpy(dtype=float)
                if row["cell_type"] in self.cell_type_offsets_.index
                else zero
            )
            rows.append(global_delta + perturb_offset + cell_offset)
        return pd.DataFrame(
            rows,
            index=dataset.metadata.index,
            columns=self.gene_names_,
            dtype=float,
        )

