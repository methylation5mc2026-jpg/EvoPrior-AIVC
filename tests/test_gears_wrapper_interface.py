from pathlib import Path

from evoprior_aivc.external.gears_wrapper import (
    probe_gears_feasibility,
    run_official_gears_or_block,
)


def test_gears_wrapper_probe_is_optional_dependency_safe():
    feasibility = probe_gears_feasibility()

    assert feasibility.decision in {
        "run_official_wrapper_now",
        "inspect_near_official_adapter",
        "document_blocker",
    }
    assert "torch" in feasibility.versions


def test_gears_wrapper_writes_blocker_when_missing(tmp_path: Path):
    config = {
        "output_root": str(tmp_path),
        "output_prefix": "out",
        "output_prefix_dry_run": "blocked",
        "benchmark_id": "toy",
        "official_wrapper": {
            "known_install_blockers": ["test blocker"],
        },
    }

    feasibility = run_official_gears_or_block(
        config=config,
        run_dir=tmp_path / "run",
        dry_run=True,
    )

    assert (tmp_path / "run" / "wrapper_feasibility.json").exists()
    assert (tmp_path / "run" / "blocker_report.md").exists()
    assert feasibility.decision in {
        "run_official_wrapper_now",
        "inspect_near_official_adapter",
        "document_blocker",
    }

