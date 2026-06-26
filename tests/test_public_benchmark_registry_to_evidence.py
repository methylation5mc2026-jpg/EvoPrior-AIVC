from pathlib import Path

import yaml

from evoprior_aivc.evaluation.benchmark_evidence import (
    collect_run_evidence,
    records_to_dataframe,
    registry_validation_to_evidence_candidates,
)
from evoprior_aivc.evaluation.benchmark_registry import load_benchmark_registry


def test_old_v010_evidence_records_still_load():
    run_dir = Path(
        "outputs/runs/v0.10-public-benchmark-alignment/"
        "kang_2018_pbmc_ifnb_alignment/20260624T021659Z"
    )
    records = collect_run_evidence(run_dir)

    assert records
    assert any(record.model_id == "lineage_shrinkage" for record in records)
    assert any(record.model_id == "public_benchmark_candidate" for record in records) is False


def test_registry_records_convert_to_blocked_evidence_candidates(tmp_path: Path):
    registry = tmp_path / "registry.yaml"
    registry.write_text(
        yaml.safe_dump(
            {
                "benchmarks": [
                    _registry_record(
                        benchmark_id="external-one",
                        evidence_status="NOT_RUN",
                    )
                ]
            }
        ),
        encoding="utf-8",
    )
    validation = load_benchmark_registry(registry)

    candidates = registry_validation_to_evidence_candidates(
        validation,
        config_path="configs/benchmarks/example.yaml",
    )
    frame = records_to_dataframe(candidates)

    assert candidates[0].evidence_status == "blocked"
    assert candidates[0].metrics == {}
    assert candidates[0].config_path == "configs/benchmarks/example.yaml"
    assert "model_run" in candidates[0].missing_artifacts
    assert frame.loc[0, "model_id"] == "public_benchmark_candidate"


def test_metadata_only_candidate_is_not_performance_evidence(tmp_path: Path):
    registry = tmp_path / "registry.yaml"
    registry.write_text(
        yaml.safe_dump({"benchmarks": [_registry_record(evidence_status="NOT_RUN")]}),
        encoding="utf-8",
    )
    validation = load_benchmark_registry(registry)

    candidate = registry_validation_to_evidence_candidates(validation)[0]

    assert candidate.evidence_status == "blocked"
    assert candidate.metrics_finite is True
    assert "Metadata registration is not benchmark evidence" in candidate.claim_boundary
    assert "metadata registration is not performance evidence" in candidate.warnings


def _registry_record(**overrides):
    record = {
        "benchmark_id": "external-metadata-only",
        "dataset_name": "External Metadata Only",
        "source_type": "paper",
        "source_url_or_reference": "metadata-only",
        "source_version_or_access_date": "2026-06-24",
        "license_or_terms": "not redistributed",
        "citation": "example citation",
        "organism": "human",
        "modality": "scRNA-seq",
        "perturbation_type": "drug",
        "cell_type_or_context": "cell line",
        "split_policy": "official split unavailable",
        "leakage_risks": ["split unavailable"],
        "local_path_status": "missing",
        "ingestion_status": "REGISTERED_METADATA_ONLY",
        "evidence_status": "NOT_RUN",
    }
    record.update(overrides)
    return record
