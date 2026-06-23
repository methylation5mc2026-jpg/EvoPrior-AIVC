"""Adapters that map real perturbation datasets to the canonical schema."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import anndata as ad
import pandas as pd
from anndata import AnnData

from evoprior_aivc.data.validate import infer_control_mask, normalize_metadata_labels, validate_adata_schema


@dataclass
class SchemaMappingReport:
    """Report produced by a real-data adapter."""

    dataset_id: str
    raw_obs_columns: list[str]
    raw_var_columns: list[str]
    canonical_mapping: dict[str, str]
    n_cells: int
    n_genes: int
    n_perturbations: int
    n_controls: int
    top_perturbation_counts: dict[str, int]
    cell_type_counts: dict[str, int]
    donor_counts: dict[str, int]
    batch_counts: dict[str, int]
    missing_required_fields: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    final_decision: str = "usable"

    def to_markdown(self) -> str:
        donor_lines = _dict_lines(self.donor_counts) if self.donor_counts else ["- unavailable"]
        batch_lines = _dict_lines(self.batch_counts) if self.batch_counts else ["- unavailable"]
        lines = [
            f"# Schema Report: {self.dataset_id}",
            "",
            f"- Final decision: **{self.final_decision}**",
            f"- Cells: {self.n_cells}",
            f"- Genes: {self.n_genes}",
            f"- Perturbations: {self.n_perturbations}",
            f"- Controls: {self.n_controls}",
            "",
            "## Raw Obs Columns",
            "",
            ", ".join(self.raw_obs_columns),
            "",
            "## Raw Var Columns",
            "",
            ", ".join(self.raw_var_columns),
            "",
            "## Canonical Mapping",
            "",
            *_dict_lines(self.canonical_mapping),
            "",
            "## Top Perturbation Counts",
            "",
            *_dict_lines(self.top_perturbation_counts),
            "",
            "## Cell Type Counts",
            "",
            *_dict_lines(self.cell_type_counts),
            "",
            "## Donor Counts",
            "",
            *donor_lines,
            "",
            "## Batch Counts",
            "",
            *batch_lines,
            "",
            "## Missing Required Fields",
            "",
            *_list_lines(self.missing_required_fields),
            "",
            "## Warnings",
            "",
            *_list_lines(self.warnings),
            "",
        ]
        return "\n".join(lines)


class BasePerturbationAdapter(ABC):
    """Base interface for real perturbation adapters."""

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config

    @abstractmethod
    def load(self, path: Path) -> tuple[AnnData, SchemaMappingReport]:
        """Load and canonicalize a dataset."""


class GenericH5ADPerturbationAdapter(BasePerturbationAdapter):
    """Generic H5AD adapter driven by config-defined obs/var mappings."""

    def load(self, path: Path) -> tuple[AnnData, SchemaMappingReport]:
        raw = ad.read_h5ad(path)
        raw_obs_columns = list(map(str, raw.obs.columns))
        raw_var_columns = list(map(str, raw.var.columns))
        mapping = self.config["adapter"]["obs_mapping"]
        var_mapping = self.config["adapter"].get("var_mapping", {})
        control_labels = tuple(self.config["adapter"].get("control_labels", ["control"]))
        warnings: list[str] = []
        canonical_mapping: dict[str, str] = {}

        adata = raw.copy()
        for canonical, source in mapping.items():
            if source is None:
                continue
            if source not in adata.obs.columns:
                raise KeyError(f"configured obs mapping is missing: {canonical} <- {source}")
            adata.obs[canonical] = adata.obs[source]
            canonical_mapping[canonical] = source

        if "cell_type" not in adata.obs.columns:
            fallback = self.config["adapter"].get("fallback_cell_type", "unknown_cell_type")
            adata.obs["cell_type"] = fallback
            canonical_mapping["cell_type"] = f"constant:{fallback}"
            warnings.append("cell_type missing; filled with fallback value")

        if "perturbation" not in adata.obs.columns:
            raise ValueError("adapter could not map a perturbation column")

        if "is_control" not in adata.obs.columns:
            adata.obs["is_control"] = infer_control_mask(adata, control_labels=control_labels)
            canonical_mapping["is_control"] = f"inferred:{','.join(control_labels)}"

        for canonical in ("donor", "batch", "tissue", "dose", "time"):
            if canonical in mapping and mapping[canonical] is not None:
                continue
            if canonical not in adata.obs.columns:
                warnings.append(f"{canonical} unavailable")

        for extra in self.config["adapter"].get("preserve_obs_fields", []):
            if extra in raw.obs.columns and extra not in adata.obs.columns:
                adata.obs[extra] = raw.obs[extra]

        if "gene_symbol" not in adata.var.columns:
            source = var_mapping.get("gene_symbol")
            if source is not None and source in adata.var.columns:
                adata.var["gene_symbol"] = adata.var[source].astype(str)
                canonical_mapping["gene_symbol"] = source
            else:
                adata.var["gene_symbol"] = adata.var_names.astype(str)
                canonical_mapping["gene_symbol"] = "var_names"

        if "gene_id" not in adata.var.columns:
            source = var_mapping.get("gene_id")
            if source is not None and source in adata.var.columns:
                adata.var["gene_id"] = adata.var[source].astype(str)
                canonical_mapping["gene_id"] = source

        normalize_metadata_labels(adata)
        validation = validate_adata_schema(adata)
        if validation.preferred_obs_missing:
            warnings.append(
                "preferred obs fields missing: " + ", ".join(validation.preferred_obs_missing)
            )

        report = _make_report(
            dataset_id=self.config["dataset"]["dataset_id"],
            adata=adata,
            raw_obs_columns=raw_obs_columns,
            raw_var_columns=raw_var_columns,
            canonical_mapping=canonical_mapping,
            warnings=warnings,
        )
        return adata, report


def adapter_from_config(config: dict[str, Any]) -> BasePerturbationAdapter:
    """Instantiate a dataset adapter from config."""
    name = config["dataset"]["adapter"]
    if name == "generic_h5ad":
        return GenericH5ADPerturbationAdapter(config)
    raise ValueError(f"unknown adapter: {name}")


def write_schema_report(report: SchemaMappingReport, output_dir: Path) -> Path:
    """Write a schema report markdown file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "schema_report.md"
    path.write_text(report.to_markdown(), encoding="utf-8")
    return path


def _make_report(
    *,
    dataset_id: str,
    adata: AnnData,
    raw_obs_columns: list[str],
    raw_var_columns: list[str],
    canonical_mapping: dict[str, str],
    warnings: list[str],
) -> SchemaMappingReport:
    perturbation_counts = adata.obs["perturbation"].value_counts().head(15)
    cell_type_counts = adata.obs["cell_type"].value_counts().head(15)
    donor_counts = adata.obs["donor"].value_counts().head(15) if "donor" in adata.obs else pd.Series()
    batch_counts = adata.obs["batch"].value_counts().head(15) if "batch" in adata.obs else pd.Series()
    final_decision = "usable with limitations" if warnings else "usable"
    return SchemaMappingReport(
        dataset_id=dataset_id,
        raw_obs_columns=raw_obs_columns,
        raw_var_columns=raw_var_columns,
        canonical_mapping=canonical_mapping,
        n_cells=adata.n_obs,
        n_genes=adata.n_vars,
        n_perturbations=int(adata.obs["perturbation"].nunique()),
        n_controls=int(adata.obs["is_control"].sum()),
        top_perturbation_counts=_series_to_int_dict(perturbation_counts),
        cell_type_counts=_series_to_int_dict(cell_type_counts),
        donor_counts=_series_to_int_dict(donor_counts),
        batch_counts=_series_to_int_dict(batch_counts),
        warnings=warnings,
        final_decision=final_decision,
    )


def _series_to_int_dict(series: pd.Series) -> dict[str, int]:
    return {str(index): int(value) for index, value in series.items()}


def _dict_lines(payload: dict[str, object]) -> list[str]:
    if not payload:
        return ["- none"]
    return [f"- `{key}`: {value}" for key, value in payload.items()]


def _list_lines(items: list[str]) -> list[str]:
    if not items:
        return ["- none"]
    return [f"- {item}" for item in items]
