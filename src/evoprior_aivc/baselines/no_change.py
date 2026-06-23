"""No-change baseline."""

from __future__ import annotations

import pandas as pd

from evoprior_aivc.baselines.base import DeltaBaseline, DeltaDataset, zeros_like_delta


class NoChangeBaseline(DeltaBaseline):
    """Predict zero perturbation delta for every query."""

    name = "no_change"

    def fit(self, dataset: DeltaDataset) -> "NoChangeBaseline":
        self.gene_names_ = dataset.gene_names
        return self

    def predict_delta(self, dataset: DeltaDataset) -> pd.DataFrame:
        return zeros_like_delta(dataset)

