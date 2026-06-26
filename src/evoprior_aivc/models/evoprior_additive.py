"""Transparent integrated additive EvoPrior model."""

from __future__ import annotations

from typing import Literal

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge

from evoprior_aivc.baselines.base import DeltaBaseline, DeltaDataset
from evoprior_aivc.priors.cell_lineage import CellTypeLineageMapper, LineageTree
from evoprior_aivc.priors.gene_prior_table import GenePriorTable

GenePriorMode = Literal["residual_additive", "disabled"]
FallbackMode = Literal["global", "perturbation"]


class EvoPriorAdditiveModel(DeltaBaseline):
    """Add global, perturbation, lineage, and optional gene-prior residual terms."""

    name = "evoprior_additive"

    def __init__(
        self,
        *,
        tree: LineageTree | None = None,
        mapper: CellTypeLineageMapper | None = None,
        gene_prior: GenePriorTable | None = None,
        tau_lineage: float = 1.5,
        alpha_shrinkage: float = 1.0,
        use_gene_prior: bool = True,
        use_lineage_prior: bool = True,
        gene_prior_mode: GenePriorMode = "residual_additive",
        fallback_mode: FallbackMode = "global",
        min_groups_per_effect: int = 1,
        seed: int = 0,
        impute_strategy: str = "median",
    ) -> None:
        if tau_lineage <= 0:
            raise ValueError("tau_lineage must be positive")
        if alpha_shrinkage < 0:
            raise ValueError("alpha_shrinkage must be non-negative")
        if gene_prior_mode not in {"residual_additive", "disabled"}:
            raise ValueError("gene_prior_mode must be residual_additive or disabled")
        if fallback_mode not in {"global", "perturbation"}:
            raise ValueError("fallback_mode must be global or perturbation")
        if min_groups_per_effect < 1:
            raise ValueError("min_groups_per_effect must be at least 1")
        self.tree = tree
        self.mapper = mapper
        self.gene_prior = gene_prior
        self.tau_lineage = tau_lineage
        self.alpha_shrinkage = alpha_shrinkage
        self.use_gene_prior = use_gene_prior
        self.use_lineage_prior = use_lineage_prior
        self.gene_prior_mode = gene_prior_mode
        self.fallback_mode = fallback_mode
        self.min_groups_per_effect = min_groups_per_effect
        self.seed = seed
        self.impute_strategy = impute_strategy

    def fit(self, dataset: DeltaDataset) -> EvoPriorAdditiveModel:
        """Fit additive components from training delta examples only."""
        if (
            "cell_type" not in dataset.metadata.columns
            or "perturbation" not in dataset.metadata.columns
        ):
            raise KeyError("dataset metadata must include cell_type and perturbation")
        self.gene_names_ = dataset.gene_names
        self.global_delta_ = dataset.observed_delta.mean(axis=0)
        self.perturbation_counts_ = dataset.metadata.groupby("perturbation").size()
        perturb_means = dataset.observed_delta.groupby(dataset.metadata["perturbation"]).mean()
        self.perturbation_component_ = perturb_means.subtract(self.global_delta_, axis=1)

        train = dataset.metadata[["cell_type", "perturbation"]].copy()
        train = train.join(dataset.observed_delta)
        self.by_perturbation_cell_: dict[str, pd.DataFrame] = {}
        self.by_perturbation_cell_counts_: dict[str, pd.Series] = {}
        for perturbation, group in train.groupby("perturbation", sort=True):
            self.by_perturbation_cell_[str(perturbation)] = group.groupby("cell_type")[
                self.gene_names_
            ].mean()
            self.by_perturbation_cell_counts_[str(perturbation)] = group.groupby("cell_type").size()

        base_components = self._predict_components(dataset, include_gene_prior=False)
        base = base_components["final_delta"]
        self.gene_prior_component_ = pd.Series(0.0, index=self.gene_names_, dtype=float)
        self.gene_prior_model_ = None
        if (
            self.use_gene_prior
            and self.gene_prior_mode == "residual_additive"
            and self.gene_prior is not None
        ):
            features = self.gene_prior.feature_matrix(
                self.gene_names_,
                impute_strategy=self.impute_strategy,  # type: ignore[arg-type]
            )
            residual = dataset.observed_delta - base
            target_series = residual.mean(axis=0)
            if np.allclose(target_series.to_numpy(dtype=float), 0.0):
                signs = np.sign(self.global_delta_.replace(0.0, np.nan)).fillna(1.0)
                target_series = 0.05 * residual.std(axis=0).fillna(0.0) * signs
            target = target_series.to_numpy(dtype=float)
            self.gene_prior_model_ = Ridge(alpha=self.alpha_shrinkage).fit(features, target)
            correction = self.gene_prior_model_.predict(features)
            self.gene_prior_component_ = pd.Series(correction, index=self.gene_names_, dtype=float)
        return self

    def predict_delta(self, dataset: DeltaDataset) -> pd.DataFrame:
        """Predict final delta."""
        return self.predict_components(dataset)["final_delta"]

    def predict_components(self, dataset: DeltaDataset) -> dict[str, pd.DataFrame]:
        """Predict additive component DataFrames."""
        return self._predict_components(dataset, include_gene_prior=True)

    def _predict_components(
        self,
        dataset: DeltaDataset,
        *,
        include_gene_prior: bool,
    ) -> dict[str, pd.DataFrame]:
        index = dataset.metadata.index
        global_rows: list[np.ndarray] = []
        perturb_rows: list[np.ndarray] = []
        lineage_rows: list[np.ndarray] = []
        gene_prior_rows: list[np.ndarray] = []
        for _, row in dataset.metadata.iterrows():
            perturbation = str(row["perturbation"])
            cell_type = str(row["cell_type"])
            global_component = self.global_delta_.to_numpy(dtype=float)
            perturbation_component = self._perturbation_component(perturbation)
            lineage_component = self._lineage_component(cell_type, perturbation)
            if include_gene_prior:
                gene_prior_component = self.gene_prior_component_.to_numpy(dtype=float)
            else:
                gene_prior_component = np.zeros(len(self.gene_names_), dtype=float)
            global_rows.append(global_component)
            perturb_rows.append(perturbation_component)
            lineage_rows.append(lineage_component)
            gene_prior_rows.append(gene_prior_component)

        components = {
            "global_component": self._frame(global_rows, index),
            "perturbation_component": self._frame(perturb_rows, index),
            "lineage_component": self._frame(lineage_rows, index),
            "gene_prior_component": self._frame(gene_prior_rows, index),
        }
        final = sum(components.values())
        components["final_delta"] = final
        return components

    def _perturbation_component(self, perturbation: str) -> np.ndarray:
        if perturbation in self.perturbation_component_.index:
            count = int(self.perturbation_counts_.loc[perturbation])
            if count >= self.min_groups_per_effect:
                return self.perturbation_component_.loc[perturbation].to_numpy(dtype=float)
        return np.zeros(len(self.gene_names_), dtype=float)

    def _lineage_component(self, cell_type: str, perturbation: str) -> np.ndarray:
        if not self.use_lineage_prior or self.tree is None:
            return np.zeros(len(self.gene_names_), dtype=float)
        if perturbation not in self.by_perturbation_cell_:
            return np.zeros(len(self.gene_names_), dtype=float)
        per_cell = self.by_perturbation_cell_[perturbation]
        counts = self.by_perturbation_cell_counts_[perturbation]
        if cell_type in per_cell.index and int(counts.loc[cell_type]) >= self.min_groups_per_effect:
            raw = per_cell.loc[cell_type].to_numpy(dtype=float)
            return raw - self._base_without_lineage(perturbation)
        weighted = self._lineage_weighted_average(cell_type, per_cell, counts)
        if weighted is None:
            return np.zeros(len(self.gene_names_), dtype=float)
        return weighted - self._base_without_lineage(perturbation)

    def _lineage_weighted_average(
        self,
        target_cell_type: str,
        per_cell: pd.DataFrame,
        counts: pd.Series,
    ) -> np.ndarray | None:
        target_node = self._map_cell_type(target_cell_type)
        if target_node is None:
            return None
        weights: list[float] = []
        values: list[np.ndarray] = []
        for train_cell_type, row in per_cell.iterrows():
            if int(counts.loc[train_cell_type]) < self.min_groups_per_effect:
                continue
            train_node = self._map_cell_type(str(train_cell_type))
            if train_node is None:
                continue
            try:
                distance = self.tree.tree_distance(target_node, train_node)
            except (KeyError, ValueError):
                continue
            weight = float(np.exp(-distance / self.tau_lineage))
            if weight > 0.0:
                weights.append(weight)
                values.append(row.to_numpy(dtype=float))
        if not weights:
            return None
        return np.average(np.vstack(values), axis=0, weights=np.asarray(weights, dtype=float))

    def _base_without_lineage(self, perturbation: str) -> np.ndarray:
        return self.global_delta_.to_numpy(dtype=float) + self._perturbation_component(perturbation)

    def _map_cell_type(self, cell_type: str) -> str | None:
        try:
            return self.mapper.map_one(cell_type) if self.mapper is not None else cell_type
        except KeyError:
            if self.fallback_mode in {"global", "perturbation"}:
                return None
            raise

    def _frame(self, rows: list[np.ndarray], index: pd.Index) -> pd.DataFrame:
        return pd.DataFrame(rows, index=index, columns=self.gene_names_, dtype=float)
