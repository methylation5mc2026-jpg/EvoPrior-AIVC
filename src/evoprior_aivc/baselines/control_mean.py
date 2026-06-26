"""Explicit matched-control mean baseline."""

from __future__ import annotations

import pandas as pd

from evoprior_aivc.baselines.base import DeltaBaseline, DeltaDataset, zeros_like_delta


class ControlMeanBaseline(DeltaBaseline):
    """Predict the matched control profile and therefore zero delta.

    The baseline records the fallback hierarchy used for matched controls. The
    actual matched control construction happens upstream in ``build_delta_dataset``.
    """

    name = "control_mean"

    def __init__(
        self,
        fallback_hierarchy: tuple[tuple[str, ...], ...] = (
            ("cell_type", "donor", "batch"),
            ("cell_type", "donor"),
            ("cell_type",),
            (),
        ),
    ) -> None:
        self.fallback_hierarchy = fallback_hierarchy

    def fit(self, dataset: DeltaDataset) -> ControlMeanBaseline:
        self.gene_names_ = dataset.gene_names
        self.available_fallbacks_ = tuple(
            fields
            for fields in self.fallback_hierarchy
            if all(field in dataset.metadata.columns for field in fields)
        )
        return self

    def predict_delta(self, dataset: DeltaDataset) -> pd.DataFrame:
        return zeros_like_delta(dataset)

