"""Build a small reviewer-facing release bundle."""

from __future__ import annotations

import argparse
import json
import subprocess
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

FORBIDDEN_PARTS = {
    ".git",
    ".venv",
    ".venv_gears",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
}
FORBIDDEN_PREFIXES = ("data/raw/", "outputs/runs/", "outputs/data_reports/")


def main() -> None:
    args = _parse_args()
    config = _load_yaml(Path(args.config))
    bundle_dir = build_release_bundle(config)
    print(bundle_dir)


def build_release_bundle(config: dict[str, Any]) -> Path:
    bundle_dir = _make_bundle_dir(config)
    bundle_dir.mkdir(parents=True, exist_ok=False)
    manifest = build_manifest(config, bundle_dir)
    _write_bundle_files(config, manifest, bundle_dir)
    if config.get("include_zip", False):
        manifest["zip_archive"] = str(_write_zip(config, bundle_dir))
        (bundle_dir / "release_manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        (bundle_dir / "release_manifest.md").write_text(
            _manifest_markdown(manifest),
            encoding="utf-8",
        )
    return bundle_dir


def build_manifest(config: dict[str, Any], bundle_dir: Path | None = None) -> dict[str, Any]:
    references = [
        {
            "path": path,
            "exists": Path(path).exists(),
            "safe_to_copy": _safe_to_copy(Path(path)),
        }
        for path in config.get("reference_files", [])
    ]
    primary = config["primary_evidence"]
    return {
        "release_id": config["release_id"],
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git_commit": _git(["rev-parse", "--short", "HEAD"]),
        "git_tags_at_head": _git(["tag", "--points-at", "HEAD"]).splitlines(),
        "rollback_tag": config["repository"]["rollback_tag"],
        "bundle_dir": str(bundle_dir) if bundle_dir is not None else "",
        "dataset": primary["dataset"],
        "dataset_md5": primary["dataset_md5"],
        "split": primary["split"],
        "config": primary["config"],
        "command": primary["command"],
        "output_dir": primary["output_dir"],
        "split_manifest": primary["split_manifest"],
        "smoke_result": primary["smoke_result"],
        "artifact_manifest": primary["artifact_manifest"],
        "metrics": primary["metrics"],
        "claim_boundary": config["claim_boundary"],
        "reference_files": references,
        "reproduction_commands": config["reproduction_commands"],
        "excluded": [
            "raw data",
            "large outputs",
            "model checkpoints",
            "virtual environments",
            "cache directories",
            ".git",
        ],
        "status": "pass" if all(item["exists"] for item in references) else "warn",
    }


def _write_bundle_files(
    config: dict[str, Any],
    manifest: dict[str, Any],
    bundle_dir: Path,
) -> None:
    (bundle_dir / "release_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (bundle_dir / "release_manifest.md").write_text(
        _manifest_markdown(manifest),
        encoding="utf-8",
    )
    (bundle_dir / "README_snapshot.md").write_text(
        Path("README.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (bundle_dir / "key_metrics_summary.md").write_text(
        _metrics_markdown(manifest),
        encoding="utf-8",
    )
    (bundle_dir / "claim_boundary.md").write_text(
        _claim_boundary_markdown(config["claim_boundary"]),
        encoding="utf-8",
    )
    (bundle_dir / "reproduction_commands.md").write_text(
        _commands_markdown(config["reproduction_commands"]),
        encoding="utf-8",
    )
    (bundle_dir / "file_index.md").write_text(
        _file_index_markdown(manifest),
        encoding="utf-8",
    )


def _write_zip(config: dict[str, Any], bundle_dir: Path) -> Path:
    archive_path = bundle_dir / "evoprior_aivc_v0.20_review_bundle.zip"
    generated = [
        "release_manifest.json",
        "release_manifest.md",
        "README_snapshot.md",
        "key_metrics_summary.md",
        "claim_boundary.md",
        "reproduction_commands.md",
        "file_index.md",
    ]
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in generated:
            archive.write(bundle_dir / name, arcname=name)
        for path_text in config.get("reference_files", []):
            path = Path(path_text)
            if path.exists() and _safe_to_copy(path):
                archive.write(path, arcname=f"references/{path_text}")
    return archive_path


def _manifest_markdown(manifest: dict[str, Any]) -> str:
    lines = [
        "# v0.20 Release Manifest",
        "",
        f"- Release ID: `{manifest['release_id']}`",
        f"- Status: `{manifest['status']}`",
        f"- Git commit: `{manifest['git_commit']}`",
        f"- Tags at HEAD: `{', '.join(manifest['git_tags_at_head'])}`",
        f"- Rollback tag: `{manifest['rollback_tag']}`",
        f"- Dataset md5: `{manifest['dataset_md5']}`",
        f"- Split: {manifest['split']}",
        f"- Output directory: `{manifest['output_dir']}`",
        f"- Smoke result: `{manifest['smoke_result']}`",
        f"- Artifact manifest: `{manifest['artifact_manifest']}`",
        "",
        "## References",
        "",
        "| path | exists | safe_to_copy |",
        "| --- | --- | --- |",
    ]
    for item in manifest["reference_files"]:
        lines.append(f"| {item['path']} | {item['exists']} | {item['safe_to_copy']} |")
    lines.extend(["", "## Excluded", ""])
    lines.extend(f"- {item}" for item in manifest["excluded"])
    lines.append("")
    return "\n".join(lines)


def _metrics_markdown(manifest: dict[str, Any]) -> str:
    metrics = manifest["metrics"]
    return "\n".join(
        [
            "# Key Metrics Summary",
            "",
            f"- Model: v0.17 residual baseline on `{manifest['split']}`",
            f"- Seeds: `{', '.join(map(str, metrics['seeds']))}`",
            f"- MAE: `{metrics['mae']}`",
            f"- MSE: `{metrics['mse']}`",
            f"- Pearson delta: `{metrics['pearson']}`",
            f"- Spearman delta: `{metrics['spearman']}`",
            "",
            "These are internal GEARS-compatible metrics, not official GEARS metrics.",
            "",
        ]
    )


def _claim_boundary_markdown(boundary: dict[str, list[str]]) -> str:
    lines = ["# Claim Boundary", "", "## Allowed", ""]
    lines.extend(f"- {item}" for item in boundary["allowed"])
    lines.extend(["", "## Forbidden", ""])
    lines.extend(f"- {item}" for item in boundary["forbidden"])
    lines.append("")
    return "\n".join(lines)


def _commands_markdown(commands: dict[str, list[str]]) -> str:
    lines = ["# Reproduction Commands", "", "## No-Data Review", "", "```powershell"]
    lines.extend(commands["no_data"])
    lines.extend(["```", "", "## With Local Data", "", "```powershell"])
    lines.extend(commands["with_local_data"])
    lines.extend(["```", ""])
    return "\n".join(lines)


def _file_index_markdown(manifest: dict[str, Any]) -> str:
    lines = [
        "# File Index",
        "",
        "| path | exists |",
        "| --- | --- |",
    ]
    for item in manifest["reference_files"]:
        lines.append(f"| {item['path']} | {item['exists']} |")
    lines.append("")
    return "\n".join(lines)


def _safe_to_copy(path: Path) -> bool:
    normalized = path.as_posix()
    if any(normalized.startswith(prefix) for prefix in FORBIDDEN_PREFIXES):
        return False
    if any(part in FORBIDDEN_PARTS for part in path.parts):
        return False
    return path.is_file() and path.stat().st_size <= 2_000_000


def _make_bundle_dir(config: dict[str, Any]) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return Path(config["output_root"]) / timestamp


def _git(args: list[str]) -> str:
    result = subprocess.run(["git", *args], check=False, capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    return parser.parse_args()


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    return payload if isinstance(payload, dict) else {}


if __name__ == "__main__":
    main()
