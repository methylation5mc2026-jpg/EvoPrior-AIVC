from pathlib import Path

import yaml

from evoprior_aivc.evaluation.benchmark_registry import (
    load_benchmark_registry,
    normalize_benchmark_id,
    summarize_registry,
)


def test_load_metadata_only_registry_without_local_paths(tmp_path: Path):
    registry = tmp_path / "registry.yaml"
    registry.write_text(
        yaml.safe_dump({"benchmarks": [_record()]}),
        encoding="utf-8",
    )

    validation = load_benchmark_registry(registry)
    summary = summarize_registry(validation)

    assert validation.is_valid
    assert validation.records[0].normalized_benchmark_id == "kang_ifnb_public"
    assert summary["n_records"] == 1
    assert summary["n_valid"] == 1


def test_missing_required_fields_are_reported(tmp_path: Path):
    registry = tmp_path / "registry.yaml"
    raw = _record()
    raw.pop("citation")
    registry.write_text(yaml.safe_dump({"benchmarks": [raw]}), encoding="utf-8")

    validation = load_benchmark_registry(registry)

    assert not validation.is_valid
    assert "missing required field: citation" in validation.records[0].errors


def test_duplicate_normalized_benchmark_id_is_reported(tmp_path: Path):
    registry = tmp_path / "registry.yaml"
    first = _record(benchmark_id="Kang IFNB Public")
    second = _record(benchmark_id="kang-ifnb-public")
    registry.write_text(yaml.safe_dump({"benchmarks": [first, second]}), encoding="utf-8")

    validation = load_benchmark_registry(registry)

    assert not validation.is_valid
    assert all("duplicate benchmark_id" in record.errors for record in validation.records)


def test_invalid_status_values_are_reported(tmp_path: Path):
    registry = tmp_path / "registry.yaml"
    raw = _record(ingestion_status="READY", evidence_status="DONE")
    registry.write_text(yaml.safe_dump({"benchmarks": [raw]}), encoding="utf-8")

    validation = load_benchmark_registry(registry)

    assert not validation.is_valid
    assert "invalid ingestion_status: READY" in validation.records[0].errors
    assert "invalid evidence_status: DONE" in validation.records[0].errors


def test_local_data_ready_requires_existing_local_paths(tmp_path: Path):
    registry = tmp_path / "registry.yaml"
    raw = _record(
        ingestion_status="LOCAL_DATA_READY",
        local_path_status="ready",
        local_paths={"h5ad": "missing/file.h5ad"},
    )
    registry.write_text(yaml.safe_dump({"benchmarks": [raw]}), encoding="utf-8")

    validation = load_benchmark_registry(registry)

    assert not validation.is_valid
    assert "missing local paths: h5ad" in validation.records[0].errors
    assert validation.records[0].local_path_checks["h5ad"] is False


def test_existing_local_fixture_path_validates(tmp_path: Path):
    fixture = tmp_path / "fixture.csv"
    fixture.write_text("cell_type,perturbation\nA,ctrl\n", encoding="utf-8")
    registry = tmp_path / "registry.yaml"
    raw = _record(
        ingestion_status="LOCAL_FIXTURE_VALIDATED",
        evidence_status="SMOKE_ONLY",
        local_path_status="fixture",
        local_paths={"metadata": "fixture.csv"},
    )
    registry.write_text(yaml.safe_dump({"benchmarks": [raw]}), encoding="utf-8")

    validation = load_benchmark_registry(registry)
    summary = summarize_registry(validation)

    assert validation.is_valid
    assert validation.records[0].local_path_checks["metadata"] is True
    assert summary["n_local_fixture_validated"] == 1


def test_unsafe_outputs_path_is_reported(tmp_path: Path):
    registry = tmp_path / "registry.yaml"
    raw = _record(local_paths={"artifact": "outputs/runs/file.csv"})
    registry.write_text(yaml.safe_dump({"benchmarks": [raw]}), encoding="utf-8")

    validation = load_benchmark_registry(registry)

    assert not validation.is_valid
    assert "unsafe local path for artifact: outputs/runs/file.csv" in validation.records[0].errors


def test_normalize_benchmark_id():
    assert normalize_benchmark_id("Kang IFN-beta Public!") == "kang_ifn_beta_public"


def _record(**overrides):
    record = {
        "benchmark_id": "Kang IFNB Public",
        "dataset_name": "Kang 2018 PBMC IFN-beta",
        "source_type": "paper",
        "source_url_or_reference": "Kang et al. 2018",
        "source_version_or_access_date": "metadata-only-2026-06-24",
        "license_or_terms": "not redistributed",
        "citation": "Kang et al. 2018",
        "organism": "human",
        "modality": "scRNA-seq",
        "perturbation_type": "cytokine stimulation",
        "cell_type_or_context": "PBMC",
        "split_policy": "project-defined held-out cell type",
        "leakage_risks": ["official public split not imported"],
        "local_path_status": "missing",
        "ingestion_status": "REGISTERED_METADATA_ONLY",
        "evidence_status": "NOT_RUN",
    }
    record.update(overrides)
    return record
