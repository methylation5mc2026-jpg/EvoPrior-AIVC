"""Additive single-gene-effect baseline for combo perturbations."""

from __future__ import annotations

import numpy as np
import pandas as pd

from evoprior_aivc.baselines.base import DeltaBaseline, DeltaDataset
from evoprior_aivc.data.gears_norman_adapter import perturbation_genes_from_encoded


class SingleEffectAdditiveComboBaseline(DeltaBaseline):
    """Predict combo deltas as the sum of available single-gene effects."""

    name = "single_effect_additive_combo"

    def __init__(self, *, missing_single_fallback: str = "global_single_mean") -> None:
        if missing_single_fallback not in {"global_single_mean", "global_mean", "zero"}:
            raise ValueError(
                "missing_single_fallback must be global_single_mean, global_mean, or zero"
            )
        self.missing_single_fallback = missing_single_fallback

    def fit(self, dataset: DeltaDataset) -> SingleEffectAdditiveComboBaseline:
        """Fit single perturbation effect means from training data only."""
        self.gene_names_ = dataset.gene_names
        self.global_mean_ = dataset.observed_delta.mean(axis=0)
        single = dataset.metadata["perturbation_type"].astype(str) == "single"
        single_effects: dict[str, pd.Series] = {}
        if single.any():
            for _, row in dataset.metadata.loc[single].iterrows():
                genes = perturbation_genes_from_encoded(row["perturbation_genes"])
                if len(genes) == 1:
                    single_effects.setdefault(genes[0], []).append(row.name)
        self.single_gene_means_ = {}
        for gene, indexes in single_effects.items():
            self.single_gene_means_[gene] = dataset.observed_delta.loc[indexes].mean(axis=0)
        if self.single_gene_means_:
            self.global_single_mean_ = pd.DataFrame(self.single_gene_means_).T.mean(axis=0)
        else:
            self.global_single_mean_ = self.global_mean_
        return self

    def predict_delta(self, dataset: DeltaDataset) -> pd.DataFrame:
        """Predict deltas for single or combo perturbations."""
        rows = []
        fallbacks = []
        for _, row in dataset.metadata.iterrows():
            genes = perturbation_genes_from_encoded(row["perturbation_genes"])
            predicted, fallback = self._predict_genes(genes)
            rows.append(predicted.to_numpy(dtype=float))
            fallbacks.append(fallback)
        self.last_prediction_fallbacks_ = pd.DataFrame(
            {
                "group_id": dataset.metadata.index.astype(str),
                "perturbation": dataset.metadata["perturbation"].astype(str).to_numpy(),
                "perturbation_type": dataset.metadata["perturbation_type"].astype(str).to_numpy(),
                "perturbation_genes": dataset.metadata["perturbation_genes"].astype(str).to_numpy(),
                "fallback_mode": fallbacks,
            }
        )
        return pd.DataFrame(
            rows,
            index=dataset.metadata.index,
            columns=self.gene_names_,
            dtype=float,
        )

    def prediction_fallbacks(self) -> pd.DataFrame:
        """Return fallback modes from the latest prediction call."""
        return getattr(self, "last_prediction_fallbacks_", pd.DataFrame())

    def _predict_genes(self, genes: tuple[str, ...]) -> tuple[pd.Series, str]:
        if not genes:
            return pd.Series(0.0, index=self.gene_names_, dtype=float), "control_zero"
        components = []
        missing = 0
        for gene in genes:
            if gene in self.single_gene_means_:
                components.append(self.single_gene_means_[gene])
            else:
                missing += 1
                components.append(self._fallback_vector())
        if not components:
            return self.global_mean_, "global_mean"
        summed = pd.DataFrame(components).sum(axis=0)
        if missing == 0:
            return summed, "all_single_effects"
        if missing == len(genes):
            return summed, "all_missing_single_effects"
        return summed, "partial_missing_single_effects"

    def _fallback_vector(self) -> pd.Series:
        if self.missing_single_fallback == "global_single_mean":
            return self.global_single_mean_
        if self.missing_single_fallback == "global_mean":
            return self.global_mean_
        return pd.Series(np.zeros(len(self.gene_names_)), index=self.gene_names_, dtype=float)
