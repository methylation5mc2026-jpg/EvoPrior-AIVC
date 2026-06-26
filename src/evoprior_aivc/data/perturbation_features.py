"""Leakage-safe perturbation metadata features for fast baseline models."""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from evoprior_aivc.data.gears_norman_adapter import perturbation_genes_from_encoded


@dataclass
class PerturbationFeatureEncoder:
    """Encode perturbation metadata without using target expression values."""

    include_cell_type: bool = True
    include_perturbation_type: bool = True
    gene_vocabulary_: tuple[str, ...] = field(default_factory=tuple, init=False)
    perturbation_types_: tuple[str, ...] = field(default_factory=tuple, init=False)
    cell_types_: tuple[str, ...] = field(default_factory=tuple, init=False)
    feature_names_: tuple[str, ...] = field(default_factory=tuple, init=False)

    def fit(self, metadata: pd.DataFrame) -> PerturbationFeatureEncoder:
        """Fit feature vocabularies from training metadata only."""
        _require_columns(metadata, {"perturbation_genes", "perturbation_type"})
        genes = sorted(
            {
                gene
                for encoded in metadata["perturbation_genes"]
                for gene in perturbation_genes_from_encoded(encoded)
            }
        )
        self.gene_vocabulary_ = tuple(genes)
        if self.include_perturbation_type:
            self.perturbation_types_ = tuple(
                sorted(set(metadata["perturbation_type"].astype(str)))
            )
        if self.include_cell_type and "cell_type" in metadata.columns:
            self.cell_types_ = tuple(sorted(set(metadata["cell_type"].astype(str))))
        self.feature_names_ = self._feature_names()
        return self

    def transform(self, metadata: pd.DataFrame) -> pd.DataFrame:
        """Transform metadata into a stable numeric feature matrix."""
        if not self.feature_names_:
            raise ValueError("PerturbationFeatureEncoder must be fitted before transform")
        _require_columns(metadata, {"perturbation_genes", "perturbation_type"})
        known_genes = set(self.gene_vocabulary_)
        records = []
        for _, row in metadata.iterrows():
            genes = perturbation_genes_from_encoded(row["perturbation_genes"])
            record = dict.fromkeys(self.feature_names_, 0.0)
            known_count = 0
            for gene in genes:
                if gene in known_genes:
                    record[f"gene::{gene}"] += 1.0
                    known_count += 1
            n_genes = len(genes)
            unknown_count = max(0, n_genes - known_count)
            record["n_perturbation_genes"] = float(n_genes)
            record["known_gene_count"] = float(known_count)
            record["unknown_gene_count"] = float(unknown_count)
            record["known_gene_fraction"] = float(known_count / n_genes) if n_genes else 0.0
            record["is_single"] = float(n_genes == 1)
            record["is_combo"] = float(n_genes > 1)
            if self.include_perturbation_type:
                perturbation_type = str(row["perturbation_type"])
                column = f"perturbation_type::{perturbation_type}"
                if column in record:
                    record[column] = 1.0
            if self.include_cell_type and self.cell_types_ and "cell_type" in metadata.columns:
                cell_type = str(row["cell_type"])
                column = f"cell_type::{cell_type}"
                if column in record:
                    record[column] = 1.0
            records.append(record)
        return pd.DataFrame.from_records(
            records,
            index=metadata.index.astype(str),
            columns=self.feature_names_,
        ).astype(float)

    def fit_transform(self, metadata: pd.DataFrame) -> pd.DataFrame:
        """Fit on metadata, then transform it."""
        return self.fit(metadata).transform(metadata)

    def manifest(self) -> dict[str, object]:
        """Return a compact JSON-serializable feature manifest."""
        return {
            "include_cell_type": self.include_cell_type,
            "include_perturbation_type": self.include_perturbation_type,
            "n_gene_features": len(self.gene_vocabulary_),
            "n_perturbation_type_features": len(self.perturbation_types_),
            "n_cell_type_features": len(self.cell_types_),
            "n_total_features": len(self.feature_names_),
            "gene_vocabulary": list(self.gene_vocabulary_),
            "perturbation_types": list(self.perturbation_types_),
            "cell_types": list(self.cell_types_),
            "feature_names": list(self.feature_names_),
        }

    def _feature_names(self) -> tuple[str, ...]:
        base = (
            "n_perturbation_genes",
            "known_gene_count",
            "unknown_gene_count",
            "known_gene_fraction",
            "is_single",
            "is_combo",
        )
        gene_features = tuple(f"gene::{gene}" for gene in self.gene_vocabulary_)
        type_features = tuple(
            f"perturbation_type::{value}" for value in self.perturbation_types_
        )
        cell_features = tuple(f"cell_type::{value}" for value in self.cell_types_)
        return base + gene_features + type_features + cell_features


def _require_columns(metadata: pd.DataFrame, columns: set[str]) -> None:
    missing = columns.difference(metadata.columns)
    if missing:
        raise KeyError(f"metadata missing columns: {', '.join(sorted(missing))}")
