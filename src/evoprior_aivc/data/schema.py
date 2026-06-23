"""Canonical schema definitions for perturbation AnnData objects."""

from __future__ import annotations

from dataclasses import dataclass

REQUIRED_OBS_FIELDS: tuple[str, ...] = ("cell_type", "perturbation", "is_control")
PREFERRED_OBS_FIELDS: tuple[str, ...] = ("donor", "batch")
OPTIONAL_OBS_FIELDS: tuple[str, ...] = ("tissue", "dose", "time")
REQUIRED_VAR_ALTERNATIVES: tuple[str, ...] = ("gene_symbol", "gene_id")
OPTIONAL_VAR_FIELDS: tuple[str, ...] = ("highly_variable", "gene_biotype")


@dataclass(frozen=True)
class SchemaValidationReport:
    """Small validation summary returned after schema checks pass."""

    n_obs: int
    n_vars: int
    obs_fields: tuple[str, ...]
    var_fields: tuple[str, ...]
    preferred_obs_missing: tuple[str, ...]

