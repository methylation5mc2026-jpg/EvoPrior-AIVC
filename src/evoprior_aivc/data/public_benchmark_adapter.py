"""Adapter contracts for public benchmark ingestion planning."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Protocol


@dataclass
class ExpectedBenchmarkInputs:
    """Expected files and schema hints for a public benchmark adapter."""

    required_files: list[str] = field(default_factory=list)
    optional_files: list[str] = field(default_factory=list)
    expected_columns: dict[str, list[str]] = field(default_factory=dict)
    expected_keys: list[str] = field(default_factory=list)
    split_policy: str = "not specified"
    leakage_risks: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dictionary."""
        return asdict(self)


@dataclass
class IngestionPlan:
    """Auditable ingestion plan emitted by an adapter."""

    benchmark_id: str
    adapter_type: str
    required_files: list[str]
    optional_files: list[str]
    expected_columns: dict[str, list[str]]
    expected_keys: list[str]
    split_policy: str
    leakage_risks: list[str]
    blocked_reasons: list[str] = field(default_factory=list)
    model_trained: bool = False
    performance_claim: bool = False

    @property
    def is_blocked(self) -> bool:
        """Return whether the plan is blocked."""
        return bool(self.blocked_reasons)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dictionary."""
        return asdict(self)


@dataclass
class AdapterValidation:
    """Non-throwing validation result for adapter checks."""

    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    checked_paths: dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dictionary."""
        return asdict(self)


class PublicBenchmarkAdapter(Protocol):
    """Protocol for public benchmark ingestion planning adapters."""

    benchmark_id: str

    def validate_metadata(self) -> AdapterValidation:
        """Validate metadata without reading large data."""

    def validate_local_files(self) -> AdapterValidation:
        """Validate local file existence without loading matrices."""

    def describe_expected_inputs(self) -> ExpectedBenchmarkInputs:
        """Describe expected input files and schema hints."""

    def build_ingestion_plan(self) -> IngestionPlan:
        """Build an auditable ingestion plan."""


class GenericManifestOnlyAdapter:
    """Adapter for metadata-only public benchmark registration."""

    adapter_type = "manifest_only"

    def __init__(self, record: dict[str, Any]) -> None:
        self.record = record
        self.benchmark_id = str(record.get("benchmark_id", "unknown_benchmark"))

    def validate_metadata(self) -> AdapterValidation:
        """Validate minimal metadata for a manifest-only benchmark."""
        errors = []
        for field_name in ("benchmark_id", "dataset_name", "source_url_or_reference"):
            if not self.record.get(field_name):
                errors.append(f"missing metadata field: {field_name}")
        return AdapterValidation(valid=not errors, errors=errors)

    def validate_local_files(self) -> AdapterValidation:
        """Manifest-only records do not require local files."""
        return AdapterValidation(
            valid=True,
            warnings=["metadata-only record; no local files required"],
        )

    def describe_expected_inputs(self) -> ExpectedBenchmarkInputs:
        """Return expected inputs from registry hints."""
        return ExpectedBenchmarkInputs(
            required_files=list(self.record.get("expected_files", [])),
            optional_files=list(self.record.get("optional_files", [])),
            expected_columns=dict(self.record.get("expected_columns", {})),
            expected_keys=list(self.record.get("expected_keys", [])),
            split_policy=str(self.record.get("split_policy", "not specified")),
            leakage_risks=list(self.record.get("leakage_risks", [])),
        )

    def build_ingestion_plan(self) -> IngestionPlan:
        """Build a metadata-only ingestion plan."""
        metadata = self.validate_metadata()
        expected = self.describe_expected_inputs()
        blocked = [] if metadata.valid else metadata.errors.copy()
        if str(self.record.get("ingestion_status", "")).startswith("BLOCKED"):
            blocked.append(str(self.record.get("ingestion_status")))
        if self.record.get("ingestion_status") == "REGISTERED_METADATA_ONLY":
            blocked.append("local data not available")
        return IngestionPlan(
            benchmark_id=self.benchmark_id,
            adapter_type=self.adapter_type,
            required_files=expected.required_files,
            optional_files=expected.optional_files,
            expected_columns=expected.expected_columns,
            expected_keys=expected.expected_keys,
            split_policy=expected.split_policy,
            leakage_risks=expected.leakage_risks,
            blocked_reasons=blocked,
        )


class LocalFixtureBenchmarkAdapter(GenericManifestOnlyAdapter):
    """Adapter for deterministic small local fixtures used by tests and smoke checks."""

    adapter_type = "local_fixture"

    def __init__(self, record: dict[str, Any], *, base_dir: str | Path) -> None:
        super().__init__(record)
        self.base_dir = Path(base_dir)

    def validate_local_files(self) -> AdapterValidation:
        """Validate declared required fixture files without reading large matrices."""
        expected = self.describe_expected_inputs()
        checked: dict[str, bool] = {}
        errors: list[str] = []
        local_paths = self.record.get("local_paths", {})
        if not isinstance(local_paths, dict):
            return AdapterValidation(valid=False, errors=["local_paths must be a mapping"])
        for required_file in expected.required_files:
            raw_path = local_paths.get(required_file, required_file)
            path = Path(str(raw_path))
            resolved = path if path.is_absolute() else self.base_dir / path
            exists = resolved.exists()
            checked[required_file] = exists
            if not exists:
                errors.append(f"missing required fixture file: {required_file}")
        return AdapterValidation(valid=not errors, errors=errors, checked_paths=checked)

    def build_ingestion_plan(self) -> IngestionPlan:
        """Build a fixture ingestion plan."""
        metadata = self.validate_metadata()
        local_files = self.validate_local_files()
        expected = self.describe_expected_inputs()
        blocked = metadata.errors + local_files.errors
        return IngestionPlan(
            benchmark_id=self.benchmark_id,
            adapter_type=self.adapter_type,
            required_files=expected.required_files,
            optional_files=expected.optional_files,
            expected_columns=expected.expected_columns,
            expected_keys=expected.expected_keys,
            split_policy=expected.split_policy,
            leakage_risks=expected.leakage_risks,
            blocked_reasons=blocked,
        )
