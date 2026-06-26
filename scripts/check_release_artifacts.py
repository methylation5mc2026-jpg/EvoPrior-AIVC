"""Check release artifact integrity."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

EXPECTED_TAG = "v0.24-github-push-and-release-or-website-integration"
ROLLBACK_TAG = "v0.23-github-publish-or-project-page-assets"
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
    "docs/V20_GITHUB_RELEASE_PLAN.md",
    "docs/V20_OFFICIAL_GEARS_DOCKER_ENV.md",
    "docs/V20_RELEASE_CHECKLIST.md",
    "docs/V20_GITHUB_ACTIONS_CI.md",
    "docs/V20_PUBLIC_REVIEW_README_MAP.md",
    "docs/V21_RELEASE_CANDIDATE_PLAN.md",
    "docs/V21_DOCKER_GEARS_TEST_REPORT.md",
    "docs/V21_PUBLIC_DATA_ACQUISITION_GUIDE.md",
    "docs/V21_GITHUB_RELEASE_NOTES.md",
    "docs/V21_CI_VALIDATION_REPORT.md",
    "docs/V22_PUBLIC_GITHUB_FINAL_CHECK.md",
    "docs/V22_REPO_SANITIZATION_REPORT.md",
    "docs/V22_GITHUB_RELEASE_NOTES_FINAL.md",
    "docs/V22_GITHUB_REPO_PROFILE.md",
    "docs/V22_PUBLIC_DEMO_GUIDE.md",
    "docs/V23_GITHUB_PUBLISH_GUIDE.md",
    "docs/V23_GITHUB_RELEASE_BODY.md",
    "docs/V23_PROJECT_PAGE_ASSETS.md",
    "docs/V23_MENTOR_REVIEW_BRIEF.md",
    "docs/V23_SHOWCASE_INDEX.md",
    "docs/V23_FINAL_PUBLICATION_CHECKLIST.md",
    "docs/V24_GITHUB_PUBLISH_STATUS.md",
    "docs/V24_GITHUB_RELEASE_DRAFT.md",
    "docs/V24_GITHUB_PUBLISH_COMMANDS.md",
    "docs/V24_WEBSITE_INTEGRATION_ASSETS.md",
    "docs/V24_POST_PUBLISH_CHECKLIST.md",
    "docs/V24_PUBLIC_LINK_AUDIT.md",
    "docs/V24_FINAL_PRESENTATION_SUMMARY.md",
    "reports/v0.24_final_presentation_summary.md",
    "reports/v0.21_release_notes.md",
    "configs/experiment/release_smoke_v019.yaml",
    "configs/release/v020_release_bundle.yaml",
    "configs/release/v021_release_bundle.yaml",
    "configs/release/v022_release_bundle.yaml",
    "configs/release/v024_release_bundle.yaml",
    ".github/workflows/ci.yml",
    "docker/Dockerfile.gears",
    "docker/README_GEARS_ENV.md",
    "scripts/run_release_smoke.py",
    "scripts/diagnose_official_gears.py",
    "scripts/check_release_artifacts.py",
    "scripts/make_release_bundle.py",
    "scripts/check_ci_workflow.py",
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
    (report_dir / "v0.24_artifact_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (report_dir / "v0.24_artifact_manifest.md").write_text(
        _markdown_report(manifest),
        encoding="utf-8",
    )
    print("reports/v0.24_artifact_manifest.json")
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
    release_bundle = _latest_release_bundle()
    if forbidden_staged:
        status = "fail"
    if not release_bundle:
        status = "fail"
    return {
        "release_id": EXPECTED_TAG,
        "status": status,
        "git_commit": _git(["rev-parse", "--short", "HEAD"]),
        "git_tag_expected": EXPECTED_TAG,
        "rollback_tag": ROLLBACK_TAG,
        "dataset_md5": DATA_MD5,
        "primary_output": PRIMARY_OUTPUT,
        "primary_output_exists": primary.exists(),
        "release_bundle_latest": release_bundle,
        "release_bundle_exists": bool(release_bundle),
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
                "python scripts/make_release_bundle.py --config "
                "configs/release/v024_release_bundle.yaml"
            ),
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


def _latest_release_bundle() -> str:
    root = Path("outputs/release/v0.24")
    if not root.exists():
        return ""
    candidates = [
        path
        for path in root.iterdir()
        if path.is_dir() and (path / "release_manifest.json").exists()
    ]
    candidates = sorted(candidates, key=lambda path: path.name, reverse=True)
    return str(candidates[0]) if candidates else ""


def _markdown_report(manifest: dict[str, Any]) -> str:
    lines = [
        "# v0.24 Artifact Manifest",
        "",
        f"- Status: `{manifest['status']}`",
        f"- Git commit: `{manifest['git_commit']}`",
        f"- Expected tag: `{manifest['git_tag_expected']}`",
        f"- Rollback tag: `{manifest['rollback_tag']}`",
        f"- Dataset md5: `{manifest['dataset_md5']}`",
        f"- Primary output: `{manifest['primary_output']}`",
        f"- Primary output exists: `{manifest['primary_output_exists']}`",
        f"- Latest release bundle: `{manifest['release_bundle_latest']}`",
        f"- Release bundle exists: `{manifest['release_bundle_exists']}`",
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
