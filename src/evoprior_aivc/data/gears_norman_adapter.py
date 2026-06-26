"""GEARS/Norman public H5AD adapter and schema reporting."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import anndata as ad
from anndata import AnnData


@dataclass(frozen=True)
class GearsNormanSchemaReport:
    """Schema summary for a Norman/GEARS-compatible H5AD."""

    dataset_id: str
    raw_obs_columns: list[str]
    raw_var_columns: list[str]
    perturbation_column: str
    cell_type_column: str | None
    batch_column: str | None
    n_cells: int
    n_genes: int
    n_controls: int
    n_perturbations: int
    n_single_perturbations: int
    n_combo_perturbations: int
    combo_gene_pair_coverage: int
    perturbation_type_counts: dict[str, int]
    top_perturbation_counts: dict[str, int]
    missing_fields: list[str]
    mapping_decisions: dict[str, str]
    warnings: list[str]

    def to_markdown(self) -> str:
        """Return a markdown schema report."""
        lines = [
            f"# v0.13 Norman Schema Report: {self.dataset_id}",
            "",
            f"- Cells: {self.n_cells}",
            f"- Genes: {self.n_genes}",
            f"- Controls: {self.n_controls}",
            f"- Perturbations: {self.n_perturbations}",
            f"- Single perturbations: {self.n_single_perturbations}",
            f"- Combo perturbations: {self.n_combo_perturbations}",
            f"- Combo gene-pair coverage: {self.combo_gene_pair_coverage}",
            "",
            "## Mapping Decisions",
            "",
            *_dict_lines(self.mapping_decisions),
            "",
            "## Perturbation Type Counts",
            "",
            *_dict_lines(self.perturbation_type_counts),
            "",
            "## Top Perturbation Counts",
            "",
            *_dict_lines(self.top_perturbation_counts),
            "",
            "## Raw Obs Columns",
            "",
            ", ".join(self.raw_obs_columns),
            "",
            "## Raw Var Columns",
            "",
            ", ".join(self.raw_var_columns),
            "",
            "## Missing Fields",
            "",
            *_list_lines(self.missing_fields),
            "",
            "## Warnings",
            "",
            *_list_lines(self.warnings),
            "",
        ]
        return "\n".join(lines)


def load_gears_norman_dataset(
    config: dict[str, Any],
    *,
    path: str | Path,
) -> tuple[AnnData, GearsNormanSchemaReport]:
    """Load and canonicalize a Norman/scPerturb H5AD."""
    raw_path = Path(path)
    adata = ad.read_h5ad(raw_path)
    raw_obs_columns = list(map(str, adata.obs.columns))
    raw_var_columns = list(map(str, adata.var.columns))
    adapter = config.get("adapter", {})
    perturbation_column = _first_existing(
        raw_obs_columns,
        adapter.get("perturbation_column_candidates", []),
    )
    if perturbation_column is None:
        raise KeyError("could not infer perturbation column for Norman H5AD")
    cell_type_column = _first_existing(
        raw_obs_columns,
        adapter.get("cell_type_column_candidates", []),
    )
    batch_column = _first_existing(
        raw_obs_columns,
        adapter.get("batch_column_candidates", []),
    )
    control_labels = set(map(_normalize_token, adapter.get("control_labels", [])))

    result = adata.copy()
    parsed = [
        parse_perturbation_label(value, control_labels=control_labels)
        for value in result.obs[perturbation_column]
    ]
    result.obs["perturbation"] = [item["perturbation"] for item in parsed]
    result.obs["perturbation_genes"] = [item["perturbation_genes"] for item in parsed]
    result.obs["perturbation_type"] = [item["perturbation_type"] for item in parsed]
    result.obs["is_control"] = result.obs["perturbation_type"] == "control"
    if cell_type_column is not None:
        result.obs["cell_type"] = result.obs[cell_type_column].astype(str)
    else:
        result.obs["cell_type"] = str(adapter.get("fallback_cell_type", "unknown_context"))
    if batch_column is not None:
        result.obs["batch"] = result.obs[batch_column].astype(str)

    if "gene_symbol" not in result.var.columns:
        result.var["gene_symbol"] = result.var_names.astype(str)

    report = _make_schema_report(
        config=config,
        adata=result,
        raw_obs_columns=raw_obs_columns,
        raw_var_columns=raw_var_columns,
        perturbation_column=perturbation_column,
        cell_type_column=cell_type_column,
        batch_column=batch_column,
    )
    return result, report


def parse_perturbation_label(
    value: object,
    *,
    control_labels: set[str] | None = None,
) -> dict[str, str]:
    """Parse Norman perturbation labels into canonical perturbation fields."""
    control_labels = control_labels or {"control", "ctrl", "nt", "non-targeting"}
    raw = str(value).strip()
    if not raw:
        return {
            "perturbation": "control",
            "perturbation_genes": "",
            "perturbation_type": "control",
        }
    tokens = _split_perturbation_tokens(raw)
    genes = [token for token in tokens if _normalize_token(token) not in control_labels]
    genes = _dedupe_preserve_order(genes)
    if not genes:
        return {
            "perturbation": "control",
            "perturbation_genes": "",
            "perturbation_type": "control",
        }
    perturbation = "+".join(genes)
    return {
        "perturbation": perturbation,
        "perturbation_genes": ";".join(genes),
        "perturbation_type": "single" if len(genes) == 1 else "combo",
    }


def perturbation_genes_from_encoded(value: object) -> tuple[str, ...]:
    """Return gene tokens from the canonical encoded perturbation_genes field."""
    text = str(value)
    if not text:
        return ()
    return tuple(token for token in text.split(";") if token)


def write_gears_norman_schema_report(
    report: GearsNormanSchemaReport,
    output_dir: Path,
) -> Path:
    """Write a Norman schema report."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "schema_report.md"
    path.write_text(report.to_markdown(), encoding="utf-8")
    return path


def _make_schema_report(
    *,
    config: dict[str, Any],
    adata: AnnData,
    raw_obs_columns: list[str],
    raw_var_columns: list[str],
    perturbation_column: str,
    cell_type_column: str | None,
    batch_column: str | None,
) -> GearsNormanSchemaReport:
    obs = adata.obs
    type_counts = obs["perturbation_type"].astype(str).value_counts()
    combo_pairs = obs.loc[obs["perturbation_type"] == "combo", "perturbation"].astype(str)
    warnings = []
    missing = []
    if cell_type_column is None:
        warnings.append("cell_type unavailable; fallback constant was used")
        missing.append("cell_type")
    if batch_column is None:
        missing.append("batch")
    mapping = {
        "perturbation": perturbation_column,
        "perturbation_genes": f"parsed:{perturbation_column}",
        "perturbation_type": f"parsed:{perturbation_column}",
        "is_control": f"parsed:{perturbation_column}",
        "cell_type": cell_type_column or "constant:fallback_cell_type",
        "batch": batch_column or "unavailable",
        "gene_symbol": "var.gene_symbol" if "gene_symbol" in raw_var_columns else "var_names",
    }
    return GearsNormanSchemaReport(
        dataset_id=config["dataset"]["dataset_id"],
        raw_obs_columns=raw_obs_columns,
        raw_var_columns=raw_var_columns,
        perturbation_column=perturbation_column,
        cell_type_column=cell_type_column,
        batch_column=batch_column,
        n_cells=int(adata.n_obs),
        n_genes=int(adata.n_vars),
        n_controls=int(obs["is_control"].sum()),
        n_perturbations=int(obs["perturbation"].nunique()),
        n_single_perturbations=int((obs["perturbation_type"] == "single").sum()),
        n_combo_perturbations=int((obs["perturbation_type"] == "combo").sum()),
        combo_gene_pair_coverage=int(combo_pairs.nunique()),
        perturbation_type_counts={str(k): int(v) for k, v in type_counts.items()},
        top_perturbation_counts={
            str(k): int(v) for k, v in obs["perturbation"].value_counts().head(20).items()
        },
        missing_fields=missing,
        mapping_decisions=mapping,
        warnings=warnings,
    )


def _split_perturbation_tokens(value: str) -> list[str]:
    separators = ["+", "|", ";", ","]
    for separator in separators:
        if separator in value:
            return [token.strip() for token in value.split(separator) if token.strip()]
    if "_" in value and value.count("_") == 1:
        left, right = value.split("_", 1)
        if left and right and not left.lower().startswith("non"):
            return [left.strip(), right.strip()]
    return [value.strip()]


def _first_existing(columns: list[str], candidates: list[str]) -> str | None:
    lower_to_original = {column.lower(): column for column in columns}
    for candidate in candidates:
        if candidate.lower() in lower_to_original:
            return lower_to_original[candidate.lower()]
    return None


def _normalize_token(value: object) -> str:
    return str(value).strip().lower().replace("_", "-").replace(" ", "-")


def _dedupe_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result = []
    for value in values:
        if value not in seen:
            result.append(value)
            seen.add(value)
    return result


def _dict_lines(payload: dict[str, object]) -> list[str]:
    if not payload:
        return ["- none"]
    return [f"- `{key}`: {value}" for key, value in payload.items()]


def _list_lines(items: list[str]) -> list[str]:
    if not items:
        return ["- none"]
    return [f"- {item}" for item in items]
