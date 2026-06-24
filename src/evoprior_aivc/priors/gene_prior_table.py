"""Versioned gene-prior feature tables."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd

NUMERIC_FEATURES: tuple[str, ...] = (
    "conservation_score",
    "gene_age_rank",
    "ortholog_count",
    "paralog_count",
    "expression_breadth",
)
BINARY_FEATURES: tuple[str, ...] = ("is_housekeeping", "is_immune_related")
CATEGORICAL_FEATURES: tuple[str, ...] = ("go_slim_category", "pathway_category")
ID_COLUMNS: tuple[str, ...] = ("gene_symbol", "gene_id")
METADATA_COLUMNS: tuple[str, ...] = ("source", "source_version")
IMPUTE_STRATEGY = Literal["median", "zero", "indicator"]


@dataclass(frozen=True)
class GenePriorValidationReport:
    """Summary of a gene-prior table validation pass."""

    n_genes: int
    id_columns: tuple[str, ...]
    numeric_features: tuple[str, ...]
    categorical_features: tuple[str, ...]
    missing_fraction: dict[str, float]
    source_values: tuple[str, ...]
    source_versions: tuple[str, ...]


@dataclass(frozen=True)
class GenePriorCoverageReport:
    """Coverage of a gene-prior table over a requested gene list."""

    n_requested: int
    n_mapped: int
    n_missing: int
    coverage_fraction: float
    missing_genes: tuple[str, ...]


class GenePriorTable:
    """A deterministic table of optional gene-level prior features."""

    def __init__(self, frame: pd.DataFrame) -> None:
        self._frame = _normalize_frame(frame)
        self._validation_report = self.validate()

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame) -> GenePriorTable:
        return cls(df)

    @classmethod
    def from_csv(cls, path: str | Path) -> GenePriorTable:
        return cls(pd.read_csv(path))

    def to_dataframe(self) -> pd.DataFrame:
        return self._frame.copy()

    @property
    def feature_columns(self) -> tuple[str, ...]:
        return tuple(
            column
            for column in (*NUMERIC_FEATURES, *BINARY_FEATURES, *CATEGORICAL_FEATURES)
            if column in self._frame.columns
        )

    def validate(self) -> GenePriorValidationReport:
        id_columns = tuple(column for column in ID_COLUMNS if column in self._frame.columns)
        if not id_columns:
            raise ValueError("gene prior table must contain gene_symbol or gene_id")
        for column in id_columns:
            values = self._frame[column].dropna().astype(str)
            duplicated = values[values.duplicated()].unique()
            if len(duplicated):
                preview = ", ".join(sorted(duplicated)[:5])
                raise ValueError(f"duplicate {column} values in gene prior table: {preview}")

        for column in NUMERIC_FEATURES:
            if column in self._frame.columns:
                values = pd.to_numeric(self._frame[column], errors="coerce")
                if column in {"conservation_score", "expression_breadth"}:
                    finite = values.dropna()
                    if ((finite < 0.0) | (finite > 1.0)).any():
                        raise ValueError(f"{column} must be in [0, 1]")
                if column in {"ortholog_count", "paralog_count", "gene_age_rank"}:
                    finite = values.dropna()
                    if (finite < 0.0).any():
                        raise ValueError(f"{column} must be non-negative")

        for column in BINARY_FEATURES:
            if column in self._frame.columns:
                finite = pd.to_numeric(self._frame[column], errors="coerce").dropna()
                if not finite.isin([0, 1]).all():
                    raise ValueError(f"{column} must be binary 0/1")

        missing_fraction = {
            column: float(self._frame[column].isna().mean())
            for column in self.feature_columns
        }
        return GenePriorValidationReport(
            n_genes=int(self._frame.shape[0]),
            id_columns=id_columns,
            numeric_features=tuple(
                column for column in (*NUMERIC_FEATURES, *BINARY_FEATURES) if column in self._frame
            ),
            categorical_features=tuple(
                column for column in CATEGORICAL_FEATURES if column in self._frame
            ),
            missing_fraction=missing_fraction,
            source_values=_unique_values(self._frame, "source"),
            source_versions=_unique_values(self._frame, "source_version"),
        )

    def coverage_for_genes(
        self,
        gene_symbols_or_ids: Sequence[str],
        *,
        id_column: str = "gene_symbol",
    ) -> GenePriorCoverageReport:
        aligned = self.align_to_genes(gene_symbols_or_ids, id_column=id_column)
        mapped = ~aligned["_prior_missing"]
        missing_genes = tuple(aligned.index[mapped == False].astype(str))  # noqa: E712
        n_requested = len(gene_symbols_or_ids)
        n_mapped = int(mapped.sum())
        return GenePriorCoverageReport(
            n_requested=n_requested,
            n_mapped=n_mapped,
            n_missing=n_requested - n_mapped,
            coverage_fraction=n_mapped / n_requested if n_requested else 0.0,
            missing_genes=missing_genes,
        )

    def align_to_genes(
        self,
        gene_symbols_or_ids: Sequence[str],
        *,
        id_column: str = "gene_symbol",
    ) -> pd.DataFrame:
        if id_column not in ID_COLUMNS:
            raise ValueError("id_column must be gene_symbol or gene_id")
        if id_column not in self._frame.columns:
            raise KeyError(f"gene prior table does not contain {id_column}")
        requested = [str(gene) for gene in gene_symbols_or_ids]
        indexed = self._frame.set_index(id_column, drop=False)
        aligned = indexed.reindex(requested)
        aligned.index = requested
        aligned["_prior_missing"] = aligned[id_column].isna()
        return aligned

    def impute_missing(
        self,
        strategy: IMPUTE_STRATEGY = "median",
    ) -> GenePriorTable:
        frame = self._frame.copy()
        frame = _impute_frame(frame, strategy=strategy)
        return GenePriorTable(frame)

    def standardize_numeric_features(self) -> GenePriorTable:
        frame = self._frame.copy()
        for column in (*NUMERIC_FEATURES, *BINARY_FEATURES):
            if column not in frame.columns:
                continue
            values = pd.to_numeric(frame[column], errors="coerce")
            std = float(values.std(ddof=0))
            if std == 0.0 or np.isnan(std):
                frame[column] = 0.0
            else:
                frame[column] = (values - float(values.mean())) / std
        return GenePriorTable(frame)

    def add_missing_indicators(self) -> GenePriorTable:
        frame = self._frame.copy()
        for column in self.feature_columns:
            frame[f"{column}_missing"] = frame[column].isna().astype(float)
        return GenePriorTable(frame)

    def feature_matrix(
        self,
        genes: Sequence[str],
        *,
        id_column: str = "gene_symbol",
        impute_strategy: IMPUTE_STRATEGY = "median",
        standardize: bool = True,
        add_missing_indicators: bool = True,
    ) -> pd.DataFrame:
        aligned = self.align_to_genes(genes, id_column=id_column)
        missing_before = aligned.loc[:, list(self.feature_columns)].isna()
        features = _impute_frame(aligned, strategy=impute_strategy)
        encoded = _encode_feature_frame(features)
        if standardize:
            encoded = _standardize_matrix(encoded)
        if add_missing_indicators:
            indicators = missing_before.astype(float).add_prefix("missing_")
            indicators.index = encoded.index
            encoded = pd.concat([encoded, indicators], axis=1)
        encoded.insert(0, "_prior_missing", aligned["_prior_missing"].astype(float))
        return encoded.sort_index(axis=1)

    def shuffled_control(self, seed: int = 0) -> GenePriorTable:
        rng = np.random.default_rng(seed)
        frame = self._frame.copy()
        feature_columns = [
            column
            for column in frame.columns
            if column not in {*ID_COLUMNS, *METADATA_COLUMNS}
        ]
        if not feature_columns:
            return GenePriorTable(frame)
        shuffled_positions = rng.permutation(frame.index.to_numpy())
        shuffled_features = frame.loc[shuffled_positions, feature_columns].reset_index(drop=True)
        frame = frame.reset_index(drop=True)
        frame.loc[:, feature_columns] = shuffled_features.to_numpy()
        if "source" in frame.columns:
            frame["source"] = frame["source"].astype(str) + "_shuffled"
        return GenePriorTable(frame)


def _normalize_frame(df: pd.DataFrame) -> pd.DataFrame:
    frame = df.copy()
    frame.columns = [str(column).strip() for column in frame.columns]
    for column in ID_COLUMNS:
        if column in frame.columns:
            frame[column] = frame[column].astype("string")
            frame[column] = frame[column].str.strip()
    for column in (*NUMERIC_FEATURES, *BINARY_FEATURES):
        if column in frame.columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    for column in CATEGORICAL_FEATURES:
        if column in frame.columns:
            frame[column] = frame[column].astype("string")
            frame[column] = frame[column].fillna("unknown").str.strip().str.lower()
    for column in METADATA_COLUMNS:
        if column in frame.columns:
            frame[column] = frame[column].astype("string").fillna("unknown")
    return frame.reset_index(drop=True)


def _impute_frame(frame: pd.DataFrame, *, strategy: IMPUTE_STRATEGY) -> pd.DataFrame:
    if strategy not in {"median", "zero", "indicator"}:
        raise ValueError("strategy must be median, zero, or indicator")
    result = frame.copy()
    numeric_columns = [
        column for column in (*NUMERIC_FEATURES, *BINARY_FEATURES) if column in result
    ]
    for column in numeric_columns:
        values = pd.to_numeric(result[column], errors="coerce")
        if strategy == "zero" or strategy == "indicator":
            fill_value = 0.0
        else:
            fill_value = float(values.median(skipna=True)) if values.notna().any() else 0.0
        result[column] = values.fillna(fill_value)
    for column in CATEGORICAL_FEATURES:
        if column in result.columns:
            result[column] = result[column].astype("string").fillna("unknown")
    return result


def _encode_feature_frame(frame: pd.DataFrame) -> pd.DataFrame:
    numeric_columns = [
        column for column in (*NUMERIC_FEATURES, *BINARY_FEATURES) if column in frame
    ]
    result = pd.DataFrame(index=frame.index)
    for column in numeric_columns:
        result[column] = pd.to_numeric(frame[column], errors="coerce").fillna(0.0)
    categorical_columns = [column for column in CATEGORICAL_FEATURES if column in frame]
    if categorical_columns:
        categories = pd.get_dummies(
            frame[categorical_columns].astype("string"),
            prefix=categorical_columns,
        )
        categories = categories.astype(float)
        result = pd.concat([result, categories], axis=1)
    return result


def _standardize_matrix(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    for column in result.columns:
        values = pd.to_numeric(result[column], errors="coerce").fillna(0.0)
        std = float(values.std(ddof=0))
        if std == 0.0 or np.isnan(std):
            result[column] = 0.0
        else:
            result[column] = (values - float(values.mean())) / std
    return result


def _unique_values(frame: pd.DataFrame, column: str) -> tuple[str, ...]:
    if column not in frame.columns:
        return ()
    return tuple(sorted(set(frame[column].dropna().astype(str))))
