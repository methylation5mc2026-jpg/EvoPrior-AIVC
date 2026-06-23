"""Lineage-distance shrinkage baseline for delta prediction."""

from __future__ import annotations

from typing import Literal

import numpy as np
import pandas as pd

from evoprior_aivc.baselines.base import DeltaBaseline, DeltaDataset
from evoprior_aivc.priors.cell_lineage import CellTypeLineageMapper, LineageTree


class LineageShrinkageBaseline(DeltaBaseline):
    """Borrow perturbation deltas from lineage-related training cell types."""

    name = "lineage_shrinkage"

    def __init__(
        self,
        *,
        tree: LineageTree,
        mapper: CellTypeLineageMapper | None = None,
        tau: float = 1.0,
        shrinkage: float = 0.8,
        fallback_mode: Literal["global", "zero"] = "global",
    ) -> None:
        if tau <= 0:
            raise ValueError("tau must be positive")
        if not 0.0 <= shrinkage <= 1.0:
            raise ValueError("shrinkage must be in [0, 1]")
        if fallback_mode not in {"global", "zero"}:
            raise ValueError("fallback_mode must be 'global' or 'zero'")
        self.tree = tree
        self.mapper = mapper
        self.tau = tau
        self.shrinkage = shrinkage
        self.fallback_mode = fallback_mode

    def fit(self, dataset: DeltaDataset) -> LineageShrinkageBaseline:
        if (
            "cell_type" not in dataset.metadata.columns
            or "perturbation" not in dataset.metadata.columns
        ):
            raise KeyError("dataset metadata must include cell_type and perturbation")
        self.gene_names_ = dataset.gene_names
        self.global_mean_ = dataset.observed_delta.mean(axis=0)
        self.perturbation_means_ = dataset.observed_delta.groupby(
            dataset.metadata["perturbation"]
        ).mean()
        self.cell_types_seen_ = tuple(sorted(set(dataset.metadata["cell_type"])))
        self.is_noop_ = len(self.cell_types_seen_) <= 1

        train = dataset.metadata[["cell_type", "perturbation"]].copy()
        train = train.join(dataset.observed_delta)
        gene_columns = dataset.gene_names
        self.by_perturbation_cell_: dict[str, pd.DataFrame] = {}
        for perturbation, group in train.groupby("perturbation", sort=True):
            self.by_perturbation_cell_[perturbation] = group.groupby("cell_type")[
                gene_columns
            ].mean()
        return self

    def predict_delta(self, dataset: DeltaDataset) -> pd.DataFrame:
        rows: list[np.ndarray] = []
        for _, row in dataset.metadata.iterrows():
            rows.append(self._predict_one(str(row["cell_type"]), str(row["perturbation"])))
        return pd.DataFrame(
            rows,
            index=dataset.metadata.index,
            columns=self.gene_names_,
            dtype=float,
        )

    def _predict_one(self, cell_type: str, perturbation: str) -> np.ndarray:
        zero = np.zeros(len(self.gene_names_), dtype=float)
        if perturbation not in self.by_perturbation_cell_:
            if self.fallback_mode == "global":
                return self.global_mean_.to_numpy(dtype=float)
            return zero

        per_cell = self.by_perturbation_cell_[perturbation]
        if cell_type in per_cell.index:
            direct = per_cell.loc[cell_type].to_numpy(dtype=float)
            global_effect = self.perturbation_means_.loc[perturbation].to_numpy(dtype=float)
            return self.shrinkage * direct + (1.0 - self.shrinkage) * global_effect

        lineage_weighted = self._lineage_weighted_average(cell_type, per_cell)
        global_effect = self.perturbation_means_.loc[perturbation].to_numpy(dtype=float)
        if lineage_weighted is None:
            return global_effect if self.fallback_mode == "global" else zero
        return self.shrinkage * lineage_weighted + (1.0 - self.shrinkage) * global_effect

    def _lineage_weighted_average(
        self,
        target_cell_type: str,
        per_cell: pd.DataFrame,
    ) -> np.ndarray | None:
        if self.is_noop_:
            return None
        target_node = self._map_cell_type(target_cell_type)
        weights: list[float] = []
        values: list[np.ndarray] = []
        for train_cell_type, row in per_cell.iterrows():
            try:
                train_node = self._map_cell_type(str(train_cell_type))
                distance = self.tree.tree_distance(target_node, train_node)
            except (KeyError, ValueError):
                continue
            weight = float(np.exp(-distance / self.tau))
            if weight > 0:
                weights.append(weight)
                values.append(row.to_numpy(dtype=float))
        if not weights:
            return None
        weight_array = np.asarray(weights, dtype=float)
        value_array = np.vstack(values)
        return np.average(value_array, axis=0, weights=weight_array)

    def _map_cell_type(self, cell_type: str) -> str:
        if self.mapper is None:
            return cell_type
        return self.mapper.map_one(cell_type)
