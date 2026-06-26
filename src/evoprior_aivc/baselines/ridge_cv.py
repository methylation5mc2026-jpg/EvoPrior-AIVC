"""Cross-validated ridge baseline."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import RidgeCV
from sklearn.preprocessing import OneHotEncoder

from evoprior_aivc.baselines.base import DeltaBaseline, DeltaDataset


class RidgeCVBaseline(DeltaBaseline):
    """Multi-output ridge with alpha selected by generalized CV."""

    name = "ridge_cv"

    def __init__(
        self,
        *,
        alphas: tuple[float, ...] = (0.01, 0.1, 1.0, 10.0, 100.0),
        categorical_columns: tuple[str, ...] = ("perturbation", "guide_id", "cell_type", "donor", "batch"),
    ) -> None:
        self.alphas = alphas
        self.categorical_columns = categorical_columns

    def fit(self, dataset: DeltaDataset) -> "RidgeCVBaseline":
        self.gene_names_ = dataset.gene_names
        self.used_categorical_columns_ = tuple(
            column for column in self.categorical_columns if column in dataset.metadata.columns
        )
        self.encoder_ = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
        self.encoder_.fit(dataset.metadata.loc[:, self.used_categorical_columns_])
        x = self._features(dataset)
        y = dataset.observed_delta.to_numpy(dtype=float)
        self.model_ = RidgeCV(alphas=np.asarray(self.alphas, dtype=float))
        self.model_.fit(x, y)
        self.selected_alpha_ = float(self.model_.alpha_)
        return self

    def predict_delta(self, dataset: DeltaDataset) -> pd.DataFrame:
        predictions = self.model_.predict(self._features(dataset))
        return pd.DataFrame(predictions, index=dataset.metadata.index, columns=self.gene_names_, dtype=float)

    def _features(self, dataset: DeltaDataset) -> np.ndarray:
        control = dataset.control_expression.to_numpy(dtype=float)
        categorical = self.encoder_.transform(dataset.metadata.loc[:, self.used_categorical_columns_])
        return np.hstack([control, categorical])

