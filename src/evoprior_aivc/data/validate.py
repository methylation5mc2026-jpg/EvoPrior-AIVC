"""Schema validation and metadata normalization for AnnData perturbation data."""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence

import numpy as np
import pandas as pd
from anndata import AnnData

from evoprior_aivc.data.schema import (
    PREFERRED_OBS_FIELDS,
    REQUIRED_OBS_FIELDS,
    REQUIRED_VAR_ALTERNATIVES,
    SchemaValidationReport,
)

DEFAULT_CONTROL_LABELS: tuple[str, ...] = (
    "control",
    "ctrl",
    "non-targeting",
    "nt",
    "vehicle",
    "mock",
)


def validate_adata_schema(
    adata: AnnData,
    required_obs: Sequence[str] | None = None,
    required_var: Sequence[str] | None = None,
) -> SchemaValidationReport:
    """Validate the minimal perturbation schema and return a compact report.

    By default, ``var`` must include at least one gene identifier column from
    ``gene_symbol`` or ``gene_id``. Passing ``required_var`` makes those fields
    mandatory instead.
    """
    if not isinstance(adata, AnnData):
        raise TypeError("adata must be an anndata.AnnData object")
    if adata.n_obs == 0 or adata.n_vars == 0:
        raise ValueError("adata must contain at least one cell and one gene")

    required_obs = tuple(required_obs or REQUIRED_OBS_FIELDS)
    _require_columns(adata.obs, required_obs, axis_name="obs")

    if required_var is None:
        if not any(field in adata.var.columns for field in REQUIRED_VAR_ALTERNATIVES):
            alternatives = " or ".join(REQUIRED_VAR_ALTERNATIVES)
            raise ValueError(f"var must contain at least one gene identifier column: {alternatives}")
    else:
        _require_columns(adata.var, tuple(required_var), axis_name="var")

    if adata.obs["cell_type"].isna().any():
        raise ValueError("obs['cell_type'] must not contain missing values")
    if adata.obs["perturbation"].isna().any():
        raise ValueError("obs['perturbation'] must not contain missing values")
    if adata.obs["is_control"].isna().any():
        raise ValueError("obs['is_control'] must not contain missing values")

    control_values = set(pd.Series(adata.obs["is_control"]).dropna().unique())
    if not control_values.issubset({True, False, np.bool_(True), np.bool_(False)}):
        raise ValueError("obs['is_control'] must be boolean")

    preferred_missing = tuple(field for field in PREFERRED_OBS_FIELDS if field not in adata.obs.columns)
    return SchemaValidationReport(
        n_obs=adata.n_obs,
        n_vars=adata.n_vars,
        obs_fields=tuple(map(str, adata.obs.columns)),
        var_fields=tuple(map(str, adata.var.columns)),
        preferred_obs_missing=preferred_missing,
    )


def normalize_metadata_labels(adata: AnnData) -> AnnData:
    """Normalize common string metadata labels in place and return ``adata``."""
    for column in ("cell_type", "perturbation", "donor", "batch", "tissue"):
        if column in adata.obs.columns:
            adata.obs[column] = adata.obs[column].astype("object").map(_normalize_label)

    if "is_control" in adata.obs.columns:
        adata.obs["is_control"] = adata.obs["is_control"].astype(bool)
    elif "perturbation" in adata.obs.columns:
        adata.obs["is_control"] = infer_control_mask(adata)

    return adata


def infer_control_mask(
    adata: AnnData,
    control_labels: Iterable[str] = DEFAULT_CONTROL_LABELS,
) -> pd.Series:
    """Infer controls from normalized perturbation labels."""
    if "perturbation" not in adata.obs.columns:
        raise KeyError("obs['perturbation'] is required to infer controls")

    normalized_controls = {_normalize_label(label) for label in control_labels}
    perturbations = adata.obs["perturbation"].map(_normalize_label)
    return pd.Series(perturbations.isin(normalized_controls).to_numpy(), index=adata.obs.index)


def _require_columns(frame: pd.DataFrame, required: Sequence[str], *, axis_name: str) -> None:
    missing = [column for column in required if column not in frame.columns]
    if missing:
        missing_list = ", ".join(missing)
        raise ValueError(f"{axis_name} is missing required columns: {missing_list}")


def _normalize_label(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text
