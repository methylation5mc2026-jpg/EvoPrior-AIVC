"""Real dataset loading entry points."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from anndata import AnnData

from evoprior_aivc.data.adapters import (
    SchemaMappingReport,
    adapter_from_config,
    write_schema_report,
)
from evoprior_aivc.data.registry import DatasetRecord, resolve_local_path


def load_real_dataset(
    config: dict[str, Any],
    *,
    schema_report_dir: Path | None = None,
) -> tuple[AnnData, SchemaMappingReport]:
    """Load a real dataset and map it to the canonical schema."""
    record = DatasetRecord.from_config(config)
    path = resolve_local_path(record, config)
    if not path.exists():
        raise FileNotFoundError(f"dataset file does not exist: {path}")

    adapter = adapter_from_config(config)
    adata, report = adapter.load(path)
    if schema_report_dir is not None:
        write_schema_report(report, schema_report_dir)
    return adata, report

