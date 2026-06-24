"""Gene-prior-aware non-neural correction wrapper."""

from __future__ import annotations

from typing import Literal

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge

from evoprior_aivc.baselines.base import DeltaBaseline, DeltaDataset
from evoprior_aivc.priors.gene_prior_table import GenePriorTable

CorrectionMode = Literal["residual_additive", "scale_multiplicative", "no_correction"]


class GenePriorCorrectionBaseline(DeltaBaseline):
    """Correct a base baseline using gene-prior features learned on training residuals."""

    name = "gene_prior_correction"

    def __init__(
        self,
        *,
        base_baseline: DeltaBaseline,
        gene_prior: GenePriorTable,
        mode: CorrectionMode = "residual_additive",
        alpha: float = 1.0,
        id_column: str = "gene_symbol",
        impute_strategy: str = "median",
    ) -> None:
        if mode not in {"residual_additive", "scale_multiplicative", "no_correction"}:
            raise ValueError("unsupported correction mode")
        if alpha < 0:
            raise ValueError("alpha must be non-negative")
        self.base_baseline = base_baseline
        self.gene_prior = gene_prior
        self.mode = mode
        self.alpha = alpha
        self.id_column = id_column
        self.impute_strategy = impute_strategy

    def fit(self, dataset: DeltaDataset) -> GenePriorCorrectionBaseline:
        self.gene_names_ = dataset.gene_names
        self.base_baseline.fit(dataset)
        base_pred = self.base_baseline.predict_delta(dataset)
        base_pred = base_pred.loc[dataset.observed_delta.index, dataset.observed_delta.columns]
        self.feature_matrix_ = self.gene_prior.feature_matrix(
            self.gene_names_,
            id_column=self.id_column,
            impute_strategy=self.impute_strategy,  # type: ignore[arg-type]
        )
        if self.mode == "no_correction":
            self.correction_ = pd.Series(0.0, index=self.gene_names_)
            self.scale_ = pd.Series(1.0, index=self.gene_names_)
            self.model_ = None
            return self

        if self.mode == "residual_additive":
            target = (dataset.observed_delta - base_pred).mean(axis=0)
            self.model_ = Ridge(alpha=self.alpha).fit(
                self.feature_matrix_,
                target.to_numpy(dtype=float),
            )
            correction = self.model_.predict(self.feature_matrix_)
            self.correction_ = pd.Series(correction, index=self.gene_names_, dtype=float)
            self.scale_ = pd.Series(1.0, index=self.gene_names_)
        else:
            numerator = dataset.observed_delta.abs().mean(axis=0)
            denominator = base_pred.abs().mean(axis=0).replace(0.0, np.nan)
            target = (numerator / denominator).replace([np.inf, -np.inf], np.nan).fillna(1.0)
            self.model_ = Ridge(alpha=self.alpha).fit(
                self.feature_matrix_,
                target.to_numpy(dtype=float),
            )
            scale = np.clip(self.model_.predict(self.feature_matrix_), a_min=0.0, a_max=10.0)
            self.scale_ = pd.Series(scale, index=self.gene_names_, dtype=float)
            self.correction_ = pd.Series(0.0, index=self.gene_names_)
        self.correction_summary_ = {
            "mean_abs_correction": float(np.mean(np.abs(self.correction_.to_numpy(dtype=float)))),
            "mean_scale": float(self.scale_.mean()),
            "mode": self.mode,
        }
        return self

    def predict_delta(self, dataset: DeltaDataset) -> pd.DataFrame:
        base_pred = self.base_baseline.predict_delta(dataset)
        base_pred = base_pred.loc[dataset.metadata.index, self.gene_names_]
        if self.mode == "no_correction":
            return base_pred
        if self.mode == "residual_additive":
            corrected = base_pred + self.correction_.loc[self.gene_names_]
        else:
            corrected = base_pred * self.scale_.loc[self.gene_names_]
        return pd.DataFrame(
            corrected.to_numpy(dtype=float),
            index=dataset.metadata.index,
            columns=self.gene_names_,
            dtype=float,
        )
