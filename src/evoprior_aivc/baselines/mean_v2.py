"""Stronger perturbation mean-delta baseline with explicit fallbacks."""

from __future__ import annotations

from typing import Literal

import numpy as np
import pandas as pd

from evoprior_aivc.baselines.base import DeltaBaseline, DeltaDataset


class PerturbationMeanDeltaBaselineV2(DeltaBaseline):
    """Predict mean delta by perturbation, then guide, then global/zero fallback."""

    name = "perturbation_mean_delta_v2"

    def __init__(self, *, fallback: Literal["guide", "global", "zero"] = "guide") -> None:
        if fallback not in {"guide", "global", "zero"}:
            raise ValueError("fallback must be 'guide', 'global', or 'zero'")
        self.fallback = fallback

    def fit(self, dataset: DeltaDataset) -> PerturbationMeanDeltaBaselineV2:
        self.gene_names_ = dataset.gene_names
        self.global_mean_ = dataset.observed_delta.mean(axis=0)
        self.perturbation_means_ = dataset.observed_delta.groupby(
            dataset.metadata["perturbation"]
        ).mean()
        self.guide_means_ = (
            dataset.observed_delta.groupby(dataset.metadata["guide_id"]).mean()
            if "guide_id" in dataset.metadata.columns
            else pd.DataFrame()
        )
        return self

    def predict_delta(self, dataset: DeltaDataset) -> pd.DataFrame:
        rows: list[np.ndarray] = []
        zero = np.zeros(len(self.gene_names_), dtype=float)
        for _, row in dataset.metadata.iterrows():
            perturbation = row["perturbation"]
            guide = row.get("guide_id")
            if perturbation in self.perturbation_means_.index:
                rows.append(self.perturbation_means_.loc[perturbation].to_numpy(dtype=float))
            elif (
                self.fallback == "guide"
                and guide is not None
                and not self.guide_means_.empty
                and guide in self.guide_means_.index
            ):
                rows.append(self.guide_means_.loc[guide].to_numpy(dtype=float))
            elif self.fallback in {"guide", "global"}:
                rows.append(self.global_mean_.to_numpy(dtype=float))
            else:
                rows.append(zero)
        return pd.DataFrame(
            rows,
            index=dataset.metadata.index,
            columns=self.gene_names_,
            dtype=float,
        )

