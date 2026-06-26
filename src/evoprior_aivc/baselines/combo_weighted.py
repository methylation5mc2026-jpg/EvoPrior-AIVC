"""Weighted combo-additive baseline for Norman-style combo perturbations."""

from __future__ import annotations

import numpy as np
import pandas as pd

from evoprior_aivc.baselines.combo_additive import SingleEffectAdditiveComboBaseline
from evoprior_aivc.data.gears_norman_adapter import perturbation_genes_from_encoded


class WeightedComboAdditiveBaseline(SingleEffectAdditiveComboBaseline):
    """Fit global weights for two-gene combo additive predictions."""

    name = "weighted_combo_additive"

    def __init__(
        self,
        *,
        ridge_alpha: float = 1.0,
        missing_single_fallback: str = "global_single_mean",
    ) -> None:
        super().__init__(missing_single_fallback=missing_single_fallback)
        self.ridge_alpha = float(ridge_alpha)

    def fit(self, dataset):
        """Fit single effects and global combo weights from training data only."""
        super().fit(dataset)
        self.weights_ = np.asarray([1.0, 1.0, 0.0], dtype=float)
        self.weight_fit_status_ = "fallback_unit_weights"
        x_rows: list[list[float]] = []
        y_rows: list[float] = []
        combo_mask = dataset.metadata["perturbation_type"].astype(str) == "combo"
        for group_id, row in dataset.metadata.loc[combo_mask].iterrows():
            genes = perturbation_genes_from_encoded(row["perturbation_genes"])
            if len(genes) != 2:
                continue
            first = self._single_effect_or_none(genes[0])
            second = self._single_effect_or_none(genes[1])
            if first is None or second is None:
                continue
            observed = dataset.observed_delta.loc[group_id].to_numpy(dtype=float)
            for a_value, b_value, target in zip(
                first.to_numpy(dtype=float),
                second.to_numpy(dtype=float),
                observed,
                strict=True,
            ):
                x_rows.append([a_value, b_value, 1.0])
                y_rows.append(float(target))
        if x_rows:
            x_matrix = np.asarray(x_rows, dtype=float)
            y_vector = np.asarray(y_rows, dtype=float)
            penalty = np.eye(3, dtype=float) * self.ridge_alpha
            penalty[2, 2] = 0.0
            system = x_matrix.T @ x_matrix + penalty
            self.weights_ = np.linalg.pinv(system) @ x_matrix.T @ y_vector
            self.weight_fit_status_ = "fit_on_train_combos"
        return self

    def _predict_genes(self, genes: tuple[str, ...]) -> tuple[pd.Series, str]:
        if len(genes) == 2:
            first = self._single_effect_or_none(genes[0])
            second = self._single_effect_or_none(genes[1])
            if first is not None and second is not None:
                weighted = self.weights_[0] * first + self.weights_[1] * second + self.weights_[2]
                return weighted, f"weighted_combo_{self.weight_fit_status_}"
        predicted, fallback = super()._predict_genes(genes)
        return predicted, f"weighted_fallback_{fallback}"

    def _single_effect_or_none(self, gene: str) -> pd.Series | None:
        return self.single_gene_means_.get(gene)

    def prediction_fallbacks(self) -> pd.DataFrame:
        """Return fallback modes and learned scalar weights."""
        frame = super().prediction_fallbacks().copy()
        if frame.empty:
            return frame
        frame["w1"] = float(self.weights_[0])
        frame["w2"] = float(self.weights_[1])
        frame["bias"] = float(self.weights_[2])
        frame["weight_fit_status"] = self.weight_fit_status_
        return frame
