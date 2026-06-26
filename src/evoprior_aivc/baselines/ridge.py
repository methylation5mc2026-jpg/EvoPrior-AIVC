"""Ridge regression baseline."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import OneHotEncoder

from evoprior_aivc.baselines.base import DeltaBaseline, DeltaDataset


class RidgeBaseline(DeltaBaseline):
    """Multi-output ridge baseline over control expression and metadata."""

    name = "ridge"

    def __init__(
        self,
        *,
        alpha: float = 1.0,
        categorical_columns: tuple[str, ...] = ("perturbation", "cell_type", "donor"),
    ) -> None:
        self.alpha = alpha
        self.categorical_columns = categorical_columns

    def fit(self, dataset: DeltaDataset) -> RidgeBaseline:
        self.gene_names_ = dataset.gene_names
        self.used_categorical_columns_ = tuple(
            column for column in self.categorical_columns if column in dataset.metadata.columns
        )
        self.encoder_ = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
        self.encoder_.fit(dataset.metadata.loc[:, self.used_categorical_columns_])
        x = self._features(dataset)
        y = dataset.observed_delta.to_numpy(dtype=float)
        self.model_ = Ridge(alpha=self.alpha, fit_intercept=True)
        self.model_.fit(x, y)
        return self

    def predict_delta(self, dataset: DeltaDataset) -> pd.DataFrame:
        x = self._features(dataset)
        predictions = self.model_.predict(x)
        return pd.DataFrame(
            predictions,
            index=dataset.metadata.index,
            columns=self.gene_names_,
            dtype=float,
        )

    def _features(self, dataset: DeltaDataset) -> np.ndarray:
        control = dataset.control_expression.to_numpy(dtype=float)
        categorical = self.encoder_.transform(
            dataset.metadata.loc[:, self.used_categorical_columns_]
        )
        return np.hstack([control, categorical])

