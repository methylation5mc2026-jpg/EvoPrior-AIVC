"""Hierarchical additive baseline with simple shrinkage."""

from __future__ import annotations

import numpy as np
import pandas as pd

from evoprior_aivc.baselines.base import DeltaBaseline, DeltaDataset


class HierarchicalAdditiveBaseline(DeltaBaseline):
    """Predict deltas with shrinkage-smoothed categorical effects."""

    name = "hierarchical_additive"

    def __init__(
        self,
        *,
        alpha: float = 5.0,
        effect_columns: tuple[str, ...] = ("perturbation", "guide_id", "cell_type", "batch"),
    ) -> None:
        if alpha < 0:
            raise ValueError("alpha must be non-negative")
        self.alpha = float(alpha)
        self.effect_columns = effect_columns

    def fit(self, dataset: DeltaDataset) -> "HierarchicalAdditiveBaseline":
        self.gene_names_ = dataset.gene_names
        self.global_mean_ = dataset.observed_delta.mean(axis=0)
        self.effect_tables_: dict[str, pd.DataFrame] = {}
        self.effect_counts_: dict[str, pd.Series] = {}
        for column in self.effect_columns:
            if column not in dataset.metadata.columns:
                continue
            means = dataset.observed_delta.groupby(dataset.metadata[column]).mean()
            counts = dataset.metadata[column].value_counts()
            shrink = counts / (counts + self.alpha)
            effects = means.subtract(self.global_mean_, axis="columns")
            effects = effects.mul(shrink, axis="index")
            self.effect_tables_[column] = effects
            self.effect_counts_[column] = counts
        return self

    def predict_delta(self, dataset: DeltaDataset) -> pd.DataFrame:
        rows: list[np.ndarray] = []
        global_delta = self.global_mean_.to_numpy(dtype=float)
        zero = np.zeros(len(self.gene_names_), dtype=float)
        for _, row in dataset.metadata.iterrows():
            prediction = global_delta.copy()
            for column, effects in self.effect_tables_.items():
                value = row[column]
                prediction += (
                    effects.loc[value].to_numpy(dtype=float) if value in effects.index else zero
                )
            rows.append(prediction)
        return pd.DataFrame(rows, index=dataset.metadata.index, columns=self.gene_names_, dtype=float)

