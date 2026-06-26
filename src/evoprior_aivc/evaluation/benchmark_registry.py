"""Metadata-first registry validation for external public benchmarks."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

REQUIRED_FIELDS = (
    "benchmark_id",
    "dataset_name",
    "source_type",
    "source_url_or_reference",
    "source_version_or_access_date",
    "license_or_terms",
    "citation",
    "organism",
    "modality",
    "perturbation_type",
    "cell_type_or_context",
    "split_policy",
    "leakage_risks",
    "local_path_status",
    "ingestion_status",
    "evidence_status",
)

INGESTION_STATUSES = {
    "REGISTERED_METADATA_ONLY",
    "LOCAL_FIXTURE_VALIDATED",
    "LOCAL_DATA_READY",
    "INGESTED",
    "BLOCKED_MISSING_DATA",
    "BLOCKED_LICENSE_OR_TERMS",
    "BLOCKED_SCHEMA_MISMATCH",
}

EVIDENCE_STATUSES = {
    "NOT_RUN",
    "SMOKE_ONLY",
    "SAME_SPLIT_COMPARABLE",
    "CROSS_DATASET_COMPARABLE",
    "BLOCKED",
}

LOCAL_DATA_REQUIRED_STATUSES = {"LOCAL_DATA_READY", "INGESTED"}
UNSAFE_PATH_PARTS = {"outputs", "__pycache__", ".pytest_cache", ".ruff_cache"}
UNSAFE_PATH_SUFFIXES = ("egg-info",)


@dataclass
class BenchmarkRegistryRecord:
    """Validated registry record with normalized id and non-fatal issues."""

    benchmark_id: str
    normalized_benchmark_id: str
    dataset_name: str | None
    ingestion_status: str | None
    evidence_status: str | None
    raw: dict[str, Any]
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    local_path_checks: dict[str, bool] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        """Return whether the record has no validation errors."""
        return not self.errors

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dictionary."""
        return asdict(self)


@dataclass
class BenchmarkRegistryValidation:
    """Validation result for a registry file."""

    registry_path: str
    records: list[BenchmarkRegistryRecord]
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """Return whether the registry and all records are valid."""
        return not self.errors and all(record.is_valid for record in self.records)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dictionary."""
        return asdict(self)


def normalize_benchmark_id(value: str) -> str:
    """Normalize a benchmark identifier for stable registry matching."""
    normalized = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return normalized or "unnamed_benchmark"


def load_benchmark_registry(
    path: str | Path,
    *,
    base_dir: str | Path | None = None,
) -> BenchmarkRegistryValidation:
    """Load and validate a benchmark registry YAML file."""
    registry_path = Path(path)
    root = Path(base_dir) if base_dir is not None else registry_path.parent
    try:
        payload = _load_yaml(registry_path)
    except Exception as exc:  # pragma: no cover - defensive path for malformed files.
        return BenchmarkRegistryValidation(
            registry_path=str(registry_path),
            records=[],
            errors=[f"failed to load registry: {exc}"],
        )
    entries = payload.get("benchmarks", []) if isinstance(payload, dict) else []
    if not isinstance(entries, list):
        return BenchmarkRegistryValidation(
            registry_path=str(registry_path),
            records=[],
            errors=["registry field benchmarks must be a list"],
        )
    records = [_validate_record(entry, root) for entry in entries]
    duplicate_errors = _duplicate_id_errors(records)
    if duplicate_errors:
        for record in records:
            if record.normalized_benchmark_id in duplicate_errors:
                record.errors.append("duplicate benchmark_id")
    return BenchmarkRegistryValidation(registry_path=str(registry_path), records=records)


def summarize_registry(validation: BenchmarkRegistryValidation) -> dict[str, int]:
    """Summarize registry validation by status and validity."""
    summary = {
        "n_records": len(validation.records),
        "n_valid": sum(record.is_valid for record in validation.records),
        "n_invalid": sum(not record.is_valid for record in validation.records),
        "n_blocked": sum(
            str(record.ingestion_status or "").startswith("BLOCKED")
            for record in validation.records
        ),
        "n_local_fixture_validated": sum(
            record.ingestion_status == "LOCAL_FIXTURE_VALIDATED"
            for record in validation.records
        ),
    }
    return summary


def _validate_record(raw: Any, root: Path) -> BenchmarkRegistryRecord:
    if not isinstance(raw, dict):
        return BenchmarkRegistryRecord(
            benchmark_id="",
            normalized_benchmark_id="unnamed_benchmark",
            dataset_name=None,
            ingestion_status=None,
            evidence_status=None,
            raw={},
            errors=["record must be a mapping"],
        )
    benchmark_id = str(raw.get("benchmark_id", ""))
    normalized = normalize_benchmark_id(benchmark_id)
    record = BenchmarkRegistryRecord(
        benchmark_id=benchmark_id,
        normalized_benchmark_id=normalized,
        dataset_name=_optional_string(raw.get("dataset_name")),
        ingestion_status=_optional_string(raw.get("ingestion_status")),
        evidence_status=_optional_string(raw.get("evidence_status")),
        raw=raw,
    )
    for field_name in REQUIRED_FIELDS:
        if field_name not in raw or _is_empty_required_value(raw[field_name]):
            record.errors.append(f"missing required field: {field_name}")
    if record.ingestion_status not in INGESTION_STATUSES:
        record.errors.append(f"invalid ingestion_status: {record.ingestion_status}")
    if record.evidence_status not in EVIDENCE_STATUSES:
        record.errors.append(f"invalid evidence_status: {record.evidence_status}")
    if not isinstance(raw.get("leakage_risks"), list):
        record.errors.append("leakage_risks must be a list")
    _validate_local_paths(record, root)
    return record


def _validate_local_paths(record: BenchmarkRegistryRecord, root: Path) -> None:
    local_paths = record.raw.get("local_paths", {})
    if local_paths is None:
        local_paths = {}
    if local_paths and not isinstance(local_paths, dict):
        record.errors.append("local_paths must be a mapping when provided")
        return
    path_values = _flatten_path_values(local_paths)
    for label, raw_path in path_values.items():
        path = Path(str(raw_path))
        resolved = path if path.is_absolute() else root / path
        if _is_unsafe_path(path):
            record.errors.append(f"unsafe local path for {label}: {raw_path}")
        record.local_path_checks[label] = resolved.exists()
    if record.ingestion_status in LOCAL_DATA_REQUIRED_STATUSES and not path_values:
        record.errors.append(
            f"local_paths required when ingestion_status is {record.ingestion_status}"
        )
    if record.ingestion_status in LOCAL_DATA_REQUIRED_STATUSES:
        missing = [label for label, exists in record.local_path_checks.items() if not exists]
        if missing:
            record.errors.append(f"missing local paths: {', '.join(sorted(missing))}")


def _flatten_path_values(local_paths: dict[str, Any]) -> dict[str, str]:
    flattened: dict[str, str] = {}
    for key, value in local_paths.items():
        if isinstance(value, str):
            flattened[key] = value
        elif isinstance(value, list):
            for index, item in enumerate(value):
                if isinstance(item, str):
                    flattened[f"{key}[{index}]"] = item
    return flattened


def _is_unsafe_path(path: Path) -> bool:
    parts = {part.lower() for part in path.parts}
    if parts & UNSAFE_PATH_PARTS:
        return True
    return any(part.lower().endswith(UNSAFE_PATH_SUFFIXES) for part in path.parts)


def _duplicate_id_errors(records: list[BenchmarkRegistryRecord]) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for record in records:
        if record.normalized_benchmark_id in seen:
            duplicates.add(record.normalized_benchmark_id)
        seen.add(record.normalized_benchmark_id)
    return duplicates


def _optional_string(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def _is_empty_required_value(value: Any) -> bool:
    return value is None or (isinstance(value, str) and value == "")


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    return payload if isinstance(payload, dict) else {}
