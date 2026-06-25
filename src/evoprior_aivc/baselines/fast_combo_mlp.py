"""Fast PCA-plus-MLP baseline for Norman-style perturbation deltas."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from evoprior_aivc.baselines.base import DeltaBaseline, DeltaDataset
from evoprior_aivc.data.perturbation_features import PerturbationFeatureEncoder


@dataclass(frozen=True)
class FastComboMLPConfig:
    """Configuration for the sklearn PCA+MLP fallback backend."""

    pca_components: int = 32
    hidden_layer_sizes: tuple[int, ...] = (64,)
    alpha: float = 0.0001
    learning_rate_init: float = 0.001
    max_iter: int = 250
    tol: float = 0.0001
    early_stopping: bool = True
    validation_fraction: float = 0.15
    n_iter_no_change: int = 20
    random_state: int = 0
    include_cell_type: bool = True
    include_perturbation_type: bool = True


class FastComboMLPPCA(DeltaBaseline):
    """Train an MLP to predict low-rank delta-expression coefficients."""

    name = "fast_combo_mlp_pca_sklearn"

    def __init__(self, config: FastComboMLPConfig | None = None, **kwargs: Any) -> None:
        if config is not None and kwargs:
            raise ValueError("pass either config or keyword arguments, not both")
        self.config = config or FastComboMLPConfig(**kwargs)

    def fit(self, dataset: DeltaDataset) -> FastComboMLPPCA:
        """Fit PCA and MLP using training examples only."""
        self._import_sklearn()
        self.gene_names_ = dataset.gene_names
        self.feature_encoder_ = PerturbationFeatureEncoder(
            include_cell_type=self.config.include_cell_type,
            include_perturbation_type=self.config.include_perturbation_type,
        )
        x_train = self.feature_encoder_.fit_transform(dataset.metadata)
        y_train = dataset.observed_delta.loc[:, self.gene_names_].to_numpy(dtype=float)
        n_components = min(
            int(self.config.pca_components),
            int(y_train.shape[0]),
            int(y_train.shape[1]),
        )
        if n_components < 1:
            raise ValueError("FastComboMLPPCA needs at least one training row and one gene")
        self.n_components_ = n_components
        self.x_scaler_ = self.StandardScaler()
        x_scaled = self.x_scaler_.fit_transform(x_train.to_numpy(dtype=float))
        self.pca_ = self.PCA(n_components=n_components, random_state=self.config.random_state)
        y_scores = self.pca_.fit_transform(y_train)
        self.y_scaler_ = self.StandardScaler()
        y_scaled = self.y_scaler_.fit_transform(y_scores)
        early_stopping = bool(self.config.early_stopping and x_scaled.shape[0] >= 10)
        self.model_ = self.MLPRegressor(
            hidden_layer_sizes=self.config.hidden_layer_sizes,
            alpha=float(self.config.alpha),
            learning_rate_init=float(self.config.learning_rate_init),
            max_iter=int(self.config.max_iter),
            tol=float(self.config.tol),
            early_stopping=early_stopping,
            validation_fraction=float(self.config.validation_fraction),
            n_iter_no_change=int(self.config.n_iter_no_change),
            random_state=int(self.config.random_state),
        )
        self.model_.fit(x_scaled, y_scaled)
        self.fit_status_ = {
            "backend": "sklearn",
            "estimator": "MLPRegressor",
            "target_reduction": "PCA",
            "n_train_examples": int(y_train.shape[0]),
            "n_genes": int(y_train.shape[1]),
            "n_components": int(self.n_components_),
            "n_features": int(x_train.shape[1]),
            "n_iter": int(getattr(self.model_, "n_iter_", 0)),
            "early_stopping": early_stopping,
            "final_loss": _safe_float(getattr(self.model_, "loss_", None)),
        }
        return self

    def predict_delta(self, dataset: DeltaDataset) -> pd.DataFrame:
        """Predict delta expression for query examples."""
        self._check_fitted()
        x_query = self.feature_encoder_.transform(dataset.metadata)
        x_scaled = self.x_scaler_.transform(x_query.to_numpy(dtype=float))
        y_scaled = self.model_.predict(x_scaled)
        y_scaled = np.asarray(y_scaled, dtype=float)
        if y_scaled.ndim == 1:
            y_scaled = y_scaled.reshape(-1, 1)
        y_scores = self.y_scaler_.inverse_transform(y_scaled)
        y_delta = self.pca_.inverse_transform(y_scores)
        return pd.DataFrame(
            y_delta,
            index=dataset.metadata.index.astype(str),
            columns=self.gene_names_,
            dtype=float,
        )

    def training_curve(self) -> pd.DataFrame:
        """Return the sklearn loss curve and optional validation scores."""
        self._check_fitted()
        losses = list(getattr(self.model_, "loss_curve_", []))
        validation_scores = getattr(self.model_, "validation_scores_", None) or []
        validation_scores = list(validation_scores)
        rows = []
        for index, loss in enumerate(losses):
            row = {"iteration": index + 1, "loss": _safe_float(loss)}
            if index < len(validation_scores):
                row["validation_score"] = _safe_float(validation_scores[index])
            rows.append(row)
        return pd.DataFrame(rows)

    def manifest(self) -> dict[str, object]:
        """Return a compact model manifest."""
        self._check_fitted()
        return {
            "name": self.name,
            "config": {
                "pca_components": self.config.pca_components,
                "hidden_layer_sizes": list(self.config.hidden_layer_sizes),
                "alpha": self.config.alpha,
                "learning_rate_init": self.config.learning_rate_init,
                "max_iter": self.config.max_iter,
                "tol": self.config.tol,
                "early_stopping": self.config.early_stopping,
                "validation_fraction": self.config.validation_fraction,
                "n_iter_no_change": self.config.n_iter_no_change,
                "random_state": self.config.random_state,
                "include_cell_type": self.config.include_cell_type,
                "include_perturbation_type": self.config.include_perturbation_type,
            },
            "fit_status": dict(self.fit_status_),
            "feature_manifest": self.feature_encoder_.manifest(),
            "explained_variance_ratio_sum": _safe_float(
                np.sum(self.pca_.explained_variance_ratio_)
            ),
        }

    @classmethod
    def _import_sklearn(cls) -> None:
        try:
            from sklearn.decomposition import PCA
            from sklearn.neural_network import MLPRegressor
            from sklearn.preprocessing import StandardScaler
        except ImportError as exc:
            raise ImportError(
                "FastComboMLPPCA requires scikit-learn when PyTorch is unavailable"
            ) from exc
        cls.PCA = PCA
        cls.MLPRegressor = MLPRegressor
        cls.StandardScaler = StandardScaler

    def _check_fitted(self) -> None:
        if not hasattr(self, "model_"):
            raise ValueError("FastComboMLPPCA must be fitted before prediction")


def _safe_float(value: object) -> float | None:
    if value is None:
        return None
    value = float(value)
    if np.isnan(value) or np.isinf(value):
        return None
    return value
