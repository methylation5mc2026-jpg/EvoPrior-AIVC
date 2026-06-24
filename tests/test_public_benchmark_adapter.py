from pathlib import Path

from evoprior_aivc.data.public_benchmark_adapter import (
    GenericManifestOnlyAdapter,
    LocalFixtureBenchmarkAdapter,
)


def test_manifest_only_adapter_builds_blocked_metadata_plan():
    adapter = GenericManifestOnlyAdapter(_record())

    metadata = adapter.validate_metadata()
    local_files = adapter.validate_local_files()
    plan = adapter.build_ingestion_plan()

    assert metadata.valid is True
    assert local_files.valid is True
    assert plan.benchmark_id == "external_metadata_only"
    assert plan.model_trained is False
    assert plan.performance_claim is False
    assert plan.is_blocked
    assert "local data not available" in plan.blocked_reasons


def test_manifest_only_adapter_reports_missing_metadata():
    record = _record()
    record.pop("dataset_name")
    adapter = GenericManifestOnlyAdapter(record)

    validation = adapter.validate_metadata()
    plan = adapter.build_ingestion_plan()

    assert validation.valid is False
    assert "missing metadata field: dataset_name" in plan.blocked_reasons


def test_local_fixture_adapter_validates_existing_fixture(tmp_path: Path):
    fixture = tmp_path / "metadata.csv"
    fixture.write_text("cell_type,perturbation\nA,ctrl\n", encoding="utf-8")
    record = _record(
        benchmark_id="fixture_public",
        ingestion_status="LOCAL_FIXTURE_VALIDATED",
        expected_files=["metadata"],
        local_paths={"metadata": "metadata.csv"},
        expected_columns={"metadata": ["cell_type", "perturbation"]},
    )
    adapter = LocalFixtureBenchmarkAdapter(record, base_dir=tmp_path)

    validation = adapter.validate_local_files()
    plan = adapter.build_ingestion_plan()

    assert validation.valid is True
    assert validation.checked_paths["metadata"] is True
    assert plan.is_blocked is False
    assert plan.expected_columns["metadata"] == ["cell_type", "perturbation"]


def test_local_fixture_adapter_reports_missing_fixture(tmp_path: Path):
    record = _record(
        benchmark_id="missing_fixture",
        ingestion_status="LOCAL_FIXTURE_VALIDATED",
        expected_files=["metadata"],
        local_paths={"metadata": "missing.csv"},
    )
    adapter = LocalFixtureBenchmarkAdapter(record, base_dir=tmp_path)

    validation = adapter.validate_local_files()
    plan = adapter.build_ingestion_plan()

    assert validation.valid is False
    assert validation.checked_paths["metadata"] is False
    assert "missing required fixture file: metadata" in plan.blocked_reasons


def test_adapter_describes_expected_inputs():
    adapter = GenericManifestOnlyAdapter(
        _record(
            expected_files=["metadata"],
            optional_files=["expression"],
            expected_columns={"metadata": ["cell_type"]},
            expected_keys=["obs", "var"],
            leakage_risks=["official split unavailable"],
        )
    )

    expected = adapter.describe_expected_inputs()

    assert expected.required_files == ["metadata"]
    assert expected.optional_files == ["expression"]
    assert expected.expected_columns["metadata"] == ["cell_type"]
    assert expected.expected_keys == ["obs", "var"]
    assert expected.leakage_risks == ["official split unavailable"]


def _record(**overrides):
    record = {
        "benchmark_id": "external_metadata_only",
        "dataset_name": "External Metadata Only",
        "source_url_or_reference": "metadata-only",
        "split_policy": "official split not imported",
        "leakage_risks": [],
        "ingestion_status": "REGISTERED_METADATA_ONLY",
    }
    record.update(overrides)
    return record
