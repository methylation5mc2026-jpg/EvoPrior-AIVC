from pathlib import Path

from scripts.check_ci_workflow import validate_ci_workflow


def test_ci_workflow_static_validation_passes():
    report = validate_ci_workflow(Path(".github/workflows/ci.yml"))

    assert report["status"] == "pass"
    assert report["yaml_valid"] is True
    assert report["validation_scope"] == "static_only_not_github_actions_runtime"


def test_ci_workflow_does_not_require_raw_data_or_heavy_benchmark():
    report = validate_ci_workflow(Path(".github/workflows/ci.yml"))

    assert "data/raw" not in report["forbidden_hits"]
    assert "run_norman_residual_multiseed.py" not in report["forbidden_hits"]
