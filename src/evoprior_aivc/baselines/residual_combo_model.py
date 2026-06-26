"""Residual correction baselines for Norman-style combo perturbations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from evoprior_aivc.baselines.base import DeltaBaseline, DeltaDataset
from evoprior_aivc.baselines.combo_additive import SingleEffectAdditiveComboBaseline
from evoprior_aivc.baselines.combo_weighted import WeightedComboAdditiveBaseline
from evoprior_aivc.data.perturbation_features import PerturbationFeatureEncoder


@dataclass(frozen=True)
class ResidualComboConfig:
    """Configuration for residual combo correction."""

    base_model: str = "weighted_combo_additive"
    residual_model: str = "pca_ridge"
    residual_scale: float = 0.5
    alpha: float = 1.0
    pca_components: int = 16
    hidden_layer_sizes: tuple[int, ...] = (64,)
    max_iter: int = 250
    random_state: int = 0
    include_cell_type: bool = True
    include_perturbation_type: bool = True
    include_split_class: bool = True
    include_base_prediction_features: bool = True
    missing_single_fallback: str = "global_single_mean"
    weighted_ridge_alpha: float = 1.0
    residual_target_shuffle_seed: int | None = None
    metadata_feature_shuffle_seed: int | None = None


class ResidualComboCorrectionBaseline(DeltaBaseline):
    """Predict additive base deltas plus a train-fitted residual correction."""

    def __init__(self, config: ResidualComboConfig | None = None, **kwargs: Any) -> None:
        if config is not None and kwargs:
            raise ValueError("pass either config or keyword arguments, not both")
        self.config = config or ResidualComboConfig(**kwargs)
        self.name = (
            f"residual_combo_{self.config.base_model}_{self.config.residual_model}"
            f"_scale_{self.config.residual_scale:g}"
        )

    def fit(self, dataset: DeltaDataset) -> ResidualComboCorrectionBaseline:
        """Fit the additive base and residual model on training data only."""
        self._import_sklearn()
        self.gene_names_ = dataset.gene_names
        self.base_model_ = self._make_base_model()
        self.base_model_.fit(dataset)
        base_delta = self.base_model_.predict_delta(dataset)
        residual_delta = dataset.observed_delta.loc[:, self.gene_names_] - base_delta
        if self.config.residual_target_shuffle_seed is not None:
            residual_delta = _shuffle_frame_rows(
                residual_delta,
                seed=int(self.config.residual_target_shuffle_seed),
            )
        self.feature_encoder_ = PerturbationFeatureEncoder(
            include_cell_type=self.config.include_cell_type,
            include_perturbation_type=self.config.include_perturbation_type,
        )
        metadata_features = self.feature_encoder_.fit_transform(dataset.metadata)
        if self.config.metadata_feature_shuffle_seed is not None:
            metadata_features = _shuffle_frame_rows(
                metadata_features,
                seed=int(self.config.metadata_feature_shuffle_seed),
            )
        self.extra_categories_ = self._fit_extra_categories(dataset.metadata)
        x_train = self._feature_frame(dataset.metadata, metadata_features, base_delta, fit=True)
        y_train = residual_delta.to_numpy(dtype=float)
        self.x_scaler_ = self.StandardScaler()
        x_scaled = self.x_scaler_.fit_transform(x_train.to_numpy(dtype=float))
        self.n_train_examples_ = int(x_scaled.shape[0])
        self.n_features_ = int(x_scaled.shape[1])
        self.n_genes_ = int(y_train.shape[1])
        self.n_components_ = min(
            int(self.config.pca_components),
            int(y_train.shape[0]),
            int(y_train.shape[1]),
        )
        self.fit_status_ = {
            "base_model": self.config.base_model,
            "residual_model": self.config.residual_model,
            "residual_scale": float(self.config.residual_scale),
            "n_train_examples": self.n_train_examples_,
            "n_features": self.n_features_,
            "n_genes": self.n_genes_,
        }
        if self.config.residual_model == "none" or self.config.residual_scale == 0:
            self.fit_status_["fit_mode"] = "base_only"
            return self
        if self.config.residual_model == "ridge":
            self.residual_estimator_ = self.Ridge(
                alpha=float(self.config.alpha),
                random_state=int(self.config.random_state),
            )
            self.residual_estimator_.fit(x_scaled, y_train)
            self.fit_status_["fit_mode"] = "direct_ridge"
            return self
        self.pca_ = self.PCA(
            n_components=max(1, self.n_components_),
            random_state=int(self.config.random_state),
        )
        y_scores = self.pca_.fit_transform(y_train)
        self.y_scaler_ = self.StandardScaler()
        y_scaled = self.y_scaler_.fit_transform(y_scores)
        if self.config.residual_model == "pca_ridge":
            self.residual_estimator_ = self.Ridge(
                alpha=float(self.config.alpha),
                random_state=int(self.config.random_state),
            )
            self.residual_estimator_.fit(x_scaled, y_scaled)
            self.fit_status_["fit_mode"] = "pca_ridge"
        elif self.config.residual_model == "mlp_pca":
            self.residual_estimator_ = self.MLPRegressor(
                hidden_layer_sizes=self.config.hidden_layer_sizes,
                alpha=float(self.config.alpha),
                max_iter=int(self.config.max_iter),
                random_state=int(self.config.random_state),
                early_stopping=x_scaled.shape[0] >= 10,
                validation_fraction=0.15,
                n_iter_no_change=20,
            )
            self.residual_estimator_.fit(x_scaled, y_scaled)
            self.fit_status_["fit_mode"] = "mlp_pca"
            self.fit_status_["n_iter"] = int(getattr(self.residual_estimator_, "n_iter_", 0))
            self.fit_status_["loss"] = _safe_float(
                getattr(self.residual_estimator_, "loss_", None)
            )
        else:
            raise ValueError(
                "residual_model must be one of none, ridge, pca_ridge, or mlp_pca"
            )
        self.fit_status_["pca_components"] = int(self.pca_.n_components_)
        self.fit_status_["pca_variance"] = _safe_float(
            np.sum(self.pca_.explained_variance_ratio_)
        )
        return self

    def predict_delta(self, dataset: DeltaDataset) -> pd.DataFrame:
        """Predict corrected delta expression."""
        self._check_fitted()
        base_delta = self.base_model_.predict_delta(dataset)
        if self.config.residual_model == "none" or self.config.residual_scale == 0:
            return base_delta
        metadata_features = self.feature_encoder_.transform(dataset.metadata)
        x_query = self._feature_frame(dataset.metadata, metadata_features, base_delta, fit=False)
        x_scaled = self.x_scaler_.transform(x_query.to_numpy(dtype=float))
        residual = self._predict_residual(x_scaled)
        corrected = base_delta.to_numpy(dtype=float) + float(self.config.residual_scale) * residual
        return pd.DataFrame(
            corrected,
            index=dataset.metadata.index.astype(str),
            columns=self.gene_names_,
            dtype=float,
        )

    def base_predict_delta(self, dataset: DeltaDataset) -> pd.DataFrame:
        """Return the fitted base prediction for diagnostics."""
        self._check_fitted()
        return self.base_model_.predict_delta(dataset)

    def manifest(self) -> dict[str, object]:
        """Return a JSON-serializable model manifest."""
        self._check_fitted()
        return {
            "name": self.name,
            "config": {
                "base_model": self.config.base_model,
                "residual_model": self.config.residual_model,
                "residual_scale": self.config.residual_scale,
                "alpha": self.config.alpha,
                "pca_components": self.config.pca_components,
                "hidden_layer_sizes": list(self.config.hidden_layer_sizes),
                "max_iter": self.config.max_iter,
                "random_state": self.config.random_state,
                "include_cell_type": self.config.include_cell_type,
                "include_perturbation_type": self.config.include_perturbation_type,
                "include_split_class": self.config.include_split_class,
                "include_base_prediction_features": self.config.include_base_prediction_features,
                "residual_target_shuffle_seed": self.config.residual_target_shuffle_seed,
                "metadata_feature_shuffle_seed": self.config.metadata_feature_shuffle_seed,
            },
            "fit_status": dict(self.fit_status_),
            "feature_manifest": self.feature_encoder_.manifest(),
            "extra_categories": dict(self.extra_categories_),
        }

    def _make_base_model(self) -> DeltaBaseline:
        if self.config.base_model == "single_effect_additive_combo":
            return SingleEffectAdditiveComboBaseline(
                missing_single_fallback=self.config.missing_single_fallback
            )
        if self.config.base_model == "weighted_combo_additive":
            return WeightedComboAdditiveBaseline(
                ridge_alpha=float(self.config.weighted_ridge_alpha),
                missing_single_fallback=self.config.missing_single_fallback,
            )
        if self.config.base_model == "zero_delta":
            return _ZeroDeltaBaseline()
        raise ValueError(
            "base_model must be single_effect_additive_combo, "
            "weighted_combo_additive, or zero_delta"
        )

    def _fit_extra_categories(self, metadata: pd.DataFrame) -> dict[str, tuple[str, ...]]:
        categories: dict[str, tuple[str, ...]] = {}
        if self.config.include_split_class and "split_class" in metadata.columns:
            categories["split_class"] = tuple(sorted(set(metadata["split_class"].astype(str))))
        return categories

    def _feature_frame(
        self,
        metadata: pd.DataFrame,
        metadata_features: pd.DataFrame,
        base_delta: pd.DataFrame,
        *,
        fit: bool,
    ) -> pd.DataFrame:
        frames = [metadata_features]
        del fit
        for column, values in self.extra_categories_.items():
            encoded = pd.DataFrame(0.0, index=metadata.index.astype(str), columns=[])
            for value in values:
                encoded[f"{column}::{value}"] = (
                    metadata[column].astype(str).to_numpy() == value
                ).astype(float)
            frames.append(encoded)
        if self.config.include_base_prediction_features:
            frames.append(_base_prediction_summary(base_delta))
        return pd.concat(frames, axis=1)

    def _predict_residual(self, x_scaled: np.ndarray) -> np.ndarray:
        if self.config.residual_model == "ridge":
            return np.asarray(self.residual_estimator_.predict(x_scaled), dtype=float)
        y_scaled = self.residual_estimator_.predict(x_scaled)
        y_scaled = np.asarray(y_scaled, dtype=float)
        if y_scaled.ndim == 1:
            y_scaled = y_scaled.reshape(-1, 1)
        y_scores = self.y_scaler_.inverse_transform(y_scaled)
        return np.asarray(self.pca_.inverse_transform(y_scores), dtype=float)

    @classmethod
    def _import_sklearn(cls) -> None:
        try:
            from sklearn.decomposition import PCA
            from sklearn.linear_model import Ridge
            from sklearn.neural_network import MLPRegressor
            from sklearn.preprocessing import StandardScaler
        except ImportError as exc:
            raise ImportError("ResidualComboCorrectionBaseline requires scikit-learn") from exc
        cls.MLPRegressor = MLPRegressor
        cls.PCA = PCA
        cls.Ridge = Ridge
        cls.StandardScaler = StandardScaler

    def _check_fitted(self) -> None:
        if not hasattr(self, "base_model_"):
            raise ValueError("ResidualComboCorrectionBaseline must be fitted before prediction")


def _base_prediction_summary(base_delta: pd.DataFrame) -> pd.DataFrame:
    values = base_delta.to_numpy(dtype=float)
    abs_values = np.abs(values)
    return pd.DataFrame(
        {
            "base_mean": values.mean(axis=1),
            "base_std": values.std(axis=1),
            "base_l1": abs_values.mean(axis=1),
            "base_l2": np.sqrt((values**2).mean(axis=1)),
            "base_max_abs": abs_values.max(axis=1),
            "base_positive_fraction": (values > 0).mean(axis=1),
        },
        index=base_delta.index.astype(str),
        dtype=float,
    )


def _shuffle_frame_rows(frame: pd.DataFrame, *, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    order = rng.permutation(frame.shape[0])
    return pd.DataFrame(
        frame.to_numpy(dtype=float)[order],
        index=frame.index,
        columns=frame.columns,
        dtype=float,
    )


def _safe_float(value: object) -> float | None:
    if value is None:
        return None
    value = float(value)
    if np.isnan(value) or np.isinf(value):
        return None
    return value


class _ZeroDeltaBaseline(DeltaBaseline):
    name = "zero_delta"

    def fit(self, dataset: DeltaDataset) -> _ZeroDeltaBaseline:
        self.gene_names_ = dataset.gene_names
        return self

    def predict_delta(self, dataset: DeltaDataset) -> pd.DataFrame:
        return pd.DataFrame(
            0.0,
            index=dataset.metadata.index.astype(str),
            columns=self.gene_names_,
        )
