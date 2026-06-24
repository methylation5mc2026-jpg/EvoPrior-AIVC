import json
from pathlib import Path

import pandas as pd
import yaml

from evoprior_aivc.evaluation.benchmark_evidence import (
    DEFAULT_CLAIM_BOUNDARY,
    collect_run_evidence,
    records_to_dataframe,
    write_evidence_outputs,
)


def test_collect_complete_run_dir_records_evidence(tmp_path: Path):
    run_dir = _write_run(
        tmp_path,
        include_component=True,
        include_coverage=True,
        claim_boundary="split-specific only",
    )
    records = collect_run_evidence(run_dir, config_path="configs/example.yaml")
    hgnc = _record(records, "evoprior_additive_hgnc_gene_prior")

    assert hgnc.dataset_id == "kang_2018_pbmc_ifnb"
    assert hgnc.split_id == "heldout_cell_type_suite:test"
    assert hgnc.config_path == "configs/example.yaml"
    assert hgnc.metrics_finite is True
    assert hgnc.evidence_status == "pass"
    assert hgnc.coverage_manifest is not None
    assert hgnc.component_audit is not None
    assert hgnc.claim_boundary == "split-specific only"
    assert hgnc.lineage_comparison_status == "beats_lineage_shrinkage"


def test_missing_component_audit_is_marked_weak_for_evoprior(tmp_path: Path):
    run_dir = _write_run(tmp_path, include_component=False, include_coverage=True)
    records = collect_run_evidence(run_dir)
    hgnc = _record(records, "evoprior_additive_hgnc_gene_prior")

    assert hgnc.evidence_status == "weak"
    assert "component_audit" in hgnc.missing_artifacts


def test_missing_coverage_manifest_is_recorded(tmp_path: Path):
    run_dir = _write_run(tmp_path, include_component=True, include_coverage=False)
    records = collect_run_evidence(run_dir)
    hgnc = _record(records, "evoprior_additive_hgnc_gene_prior")

    assert hgnc.coverage_manifest is None
    assert "coverage_manifest" in hgnc.missing_artifacts


def test_nonfinite_metric_marks_record_invalid(tmp_path: Path):
    run_dir = _write_run(tmp_path, include_component=True, include_coverage=True)
    metric_path = run_dir / "metric_summary.csv"
    frame = pd.read_csv(metric_path)
    frame["mean"] = frame["mean"].astype(object)
    frame.loc[frame["baseline"] == "evoprior_additive_hgnc_gene_prior", "mean"] = "inf"
    frame.to_csv(metric_path, index=False)

    hgnc = _record(collect_run_evidence(run_dir), "evoprior_additive_hgnc_gene_prior")

    assert hgnc.metrics_finite is False
    assert hgnc.evidence_status == "invalid"
    assert hgnc.warnings


def test_no_gene_prior_comparison_status_is_recorded(tmp_path: Path):
    run_dir = _write_run(tmp_path, include_component=True, include_coverage=True)
    records = collect_run_evidence(run_dir)
    hgnc = _record(records, "evoprior_additive_hgnc_gene_prior")
    no_gene = _record(records, "evoprior_additive_no_gene_prior")

    assert hgnc.gene_prior_comparison_status == "trails_no_gene_prior"
    assert no_gene.gene_prior_comparison_status == "not_applicable"
    assert hgnc.shuffled_control_status == "present"


def test_write_evidence_outputs(tmp_path: Path):
    run_dir = _write_run(tmp_path / "input", include_component=True, include_coverage=True)
    records = collect_run_evidence(run_dir)
    out_dir = tmp_path / "evidence"

    write_evidence_outputs(records, out_dir, title="Test Evidence")

    assert (out_dir / "benchmark_evidence.json").exists()
    assert (out_dir / "benchmark_evidence_table.csv").exists()
    assert (out_dir / "benchmark_evidence_report.md").exists()
    table = records_to_dataframe(records)
    assert "mae_delta_mean" in table.columns


def test_missing_claim_boundary_uses_conservative_default(tmp_path: Path):
    run_dir = _write_run(
        tmp_path,
        include_component=True,
        include_coverage=True,
        claim_boundary=None,
    )
    manifest = json.loads((run_dir / "run_manifest.json").read_text(encoding="utf-8"))
    manifest.pop("claim_boundary", None)
    (run_dir / "run_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    config = yaml.safe_load((run_dir / "resolved_config.yaml").read_text(encoding="utf-8"))
    config.pop("reporting", None)
    (run_dir / "resolved_config.yaml").write_text(yaml.safe_dump(config), encoding="utf-8")

    hgnc = _record(collect_run_evidence(run_dir), "evoprior_additive_hgnc_gene_prior")

    assert hgnc.claim_boundary == DEFAULT_CLAIM_BOUNDARY


def _write_run(
    tmp_path: Path,
    *,
    include_component: bool,
    include_coverage: bool,
    claim_boundary: str | None = "default claim boundary",
) -> Path:
    run_dir = tmp_path / "run"
    run_dir.mkdir(parents=True)
    metric_summary = pd.DataFrame(
        [
            _metric_row("lineage_shrinkage", 0.316),
            _metric_row("evoprior_additive_no_gene_prior", 0.300),
            _metric_row("evoprior_additive_hgnc_gene_prior", 0.301),
            _metric_row("evoprior_additive_shuffled_gene_prior", 0.302),
        ]
    )
    metric_summary.to_csv(run_dir / "metric_summary.csv", index=False)
    manifest = {
        "dataset_id": "kang_2018_pbmc_ifnb",
        "claim_boundary": claim_boundary,
    }
    if include_coverage:
        manifest["gene_prior_coverage"] = {"coverage_fraction": 0.9375}
    (run_dir / "run_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    config = {
        "dataset_id": "kang_2018_pbmc_ifnb",
        "reporting": {"claim_boundary": claim_boundary},
    }
    (run_dir / "resolved_config.yaml").write_text(yaml.safe_dump(config), encoding="utf-8")
    (run_dir / "split_manifest.csv").write_text("group_id,split\nx,test\n", encoding="utf-8")
    if include_component:
        summary = {
            "gene_prior_mean_abs": 0.1,
            "lineage_mean_abs": 0.2,
            "gene_prior_collapsed": False,
        }
        (run_dir / "component_audit_summary.json").write_text(
            json.dumps(summary),
            encoding="utf-8",
        )
        (run_dir / "component_audit.md").write_text("# audit\n", encoding="utf-8")
    return run_dir


def _metric_row(baseline: str, mae: float) -> dict[str, object]:
    return {
        "split_mode": "heldout_cell_type_suite",
        "split": "test",
        "baseline": baseline,
        "metric": "mae_delta",
        "n": 7,
        "mean": mae,
        "std": 0.1,
        "ci_low": mae - 0.1,
        "ci_high": mae + 0.1,
        "underpowered": False,
    }


def _record(records, model_id: str):
    return next(record for record in records if record.model_id == model_id)
