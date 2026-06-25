"""Check v0.19 release artifact integrity."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

EXPECTED_TAG = "v0.19-public-repo-polish-and-official-gears-unblock"
PRIMARY_OUTPUT = (
    "outputs/runs/v0.17-norman-validated-residual-baseline/"
    "gears_norman_scperturb_v013/20260625T100322Z"
)
DATA_MD5 = "c870e6967d91c017d9da827bab183cd6"

REQUIRED_FILES = [
    "README.md",
    "LICENSE",
    "CITATION.cff",
    "CONTRIBUTING.md",
    "SECURITY.md",
    ".env.example",
    "docs/V18_RELEASE_MODEL_CARD.md",
    "docs/V18_BENCHMARK_CARD.md",
    "docs/V18_REPRODUCIBILITY_RUNBOOK.md",
    "docs/V18_EXTERNAL_REVIEW_INDEX.md",
    "docs/V19_PUBLIC_REPO_REVIEW_CHECKLIST.md",
    "docs/V19_OFFICIAL_GEARS_UNBLOCK_PLAN.md",
    "docs/V19_REPRODUCTION_SMOKE_TESTS.md",
    "docs/V19_APPLICATION_PORTFOLIO_SUMMARY.md",
    "configs/experiment/release_smoke_v019.yaml",
    "scripts/run_release_smoke.py",
    "scripts/diagnose_official_gears.py",
    "scripts/check_release_artifacts.py",
]

METRIC_FILES = [
    "aggregate_metrics.csv",
    "comparison_to_v014_v015_v016.csv",
    "ablation_summary.csv",
    "leakage_stress_checks.csv",
    "per_class_metric_summary.csv",
]

FORBIDDEN_STAGED_PREFIXES = (
    "data/raw/",
    "outputs/",
    ".venv",
    ".tmp_",
    ".pytest_cache/",
    ".ruff_cache/",
)


def main() -> None:
    manifest = build_manifest()
    report_dir = Path("reports")
    report_dir.mkdir(exist_ok=True)
    (report_dir / "v0.19_artifact_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (report_dir / "v0.19_artifact_manifest.md").write_text(
        _markdown_report(manifest),
        encoding="utf-8",
    )
    print("reports/v0.19_artifact_manifest.json")
    print(manifest["status"])
    if manifest["status"] != "pass":
        raise SystemExit(1)


def build_manifest() -> dict[str, Any]:
    required = [{"path": path, "exists": Path(path).exists()} for path in REQUIRED_FILES]
    primary = Path(PRIMARY_OUTPUT)
    metrics = [
        {"path": str(primary / name), "exists": (primary / name).exists()}
        for name in METRIC_FILES
    ]
    staged = _staged_files()
    forbidden_staged = [
        path
        for path in staged
        if any(path.replace("\\", "/").startswith(prefix) for prefix in FORBIDDEN_STAGED_PREFIXES)
    ]
    status = "pass"
    if any(not item["exists"] for item in required):
        status = "fail"
    if primary.exists() and any(not item["exists"] for item in metrics):
        status = "fail"
    if forbidden_staged:
        status = "fail"
    return {
        "release_id": EXPECTED_TAG,
        "status": status,
        "git_commit": _git(["rev-parse", "--short", "HEAD"]),
        "git_tag_expected": EXPECTED_TAG,
        "dataset_md5": DATA_MD5,
        "primary_output": PRIMARY_OUTPUT,
        "primary_output_exists": primary.exists(),
        "required_files": required,
        "metric_files": metrics,
        "staged_files_checked": staged,
        "forbidden_staged_files": forbidden_staged,
        "reproduction_commands": [
            (
                "python scripts/run_release_smoke.py --config "
                "configs/experiment/release_smoke_v019.yaml"
            ),
            "python scripts/diagnose_official_gears.py",
            "python scripts/check_release_artifacts.py",
            (
                "python scripts/run_norman_residual_multiseed.py --config "
                "configs/experiment/gears_norman_v017_multiseed_residual.yaml"
            ),
        ],
        "not_included": ["raw data", "outputs", "virtual environments", "cache directories"],
    }


def _staged_files() -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        check=False,
        capture_output=True,
        text=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _git(args: list[str]) -> str:
    result = subprocess.run(["git", *args], check=False, capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def _markdown_report(manifest: dict[str, Any]) -> str:
    lines = [
        "# v0.19 Artifact Manifest",
        "",
        f"- Status: `{manifest['status']}`",
        f"- Git commit: `{manifest['git_commit']}`",
        f"- Expected tag: `{manifest['git_tag_expected']}`",
        f"- Dataset md5: `{manifest['dataset_md5']}`",
        f"- Primary output: `{manifest['primary_output']}`",
        f"- Primary output exists: `{manifest['primary_output_exists']}`",
        "",
        "## Required Files",
        "",
        "| path | exists |",
        "| --- | --- |",
    ]
    for item in manifest["required_files"]:
        lines.append(f"| {item['path']} | {item['exists']} |")
    lines.extend(["", "## Metric Files", "", "| path | exists |", "| --- | --- |"])
    for item in manifest["metric_files"]:
        lines.append(f"| {item['path']} | {item['exists']} |")
    lines.extend(
        [
            "",
            "## Forbidden Staged Files",
            "",
            str(manifest["forbidden_staged_files"]),
            "",
            "Raw data, outputs, virtual environments, and caches are not release artifacts.",
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
