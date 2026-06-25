"""Static validation for the GitHub Actions smoke workflow."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

FORBIDDEN_SNIPPETS = (
    "data/raw",
    "NormanWeissman2019_filtered.h5ad",
    "run_norman_residual_multiseed.py",
    "docker build",
    "torch",
    "gears_norman_v017_multiseed_residual.yaml",
)

REQUIRED_REFERENCES = (
    "tests/test_release_smoke_config.py",
    "tests/test_release_artifact_manifest.py",
    "tests/test_official_gears_diagnostics.py",
    "scripts/run_release_smoke.py",
    "configs/experiment/release_smoke_v019.yaml",
)


def main() -> None:
    args = _parse_args()
    report = validate_ci_workflow(Path(args.workflow))
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if report["status"] != "pass":
        raise SystemExit(1)


def validate_ci_workflow(path: Path) -> dict[str, Any]:
    exists = path.exists()
    text = path.read_text(encoding="utf-8") if exists else ""
    parsed = _parse_yaml(text) if exists else None
    missing_refs = [item for item in REQUIRED_REFERENCES if item not in text]
    forbidden_hits = [item for item in FORBIDDEN_SNIPPETS if item in text]
    referenced_paths = _referenced_paths(text)
    missing_paths = [item for item in referenced_paths if not Path(item).exists()]
    status = "pass"
    if not exists or parsed is None or missing_refs or forbidden_hits or missing_paths:
        status = "fail"
    return {
        "status": status,
        "workflow": str(path),
        "exists": exists,
        "yaml_valid": parsed is not None,
        "missing_required_references": missing_refs,
        "forbidden_hits": forbidden_hits,
        "referenced_paths": referenced_paths,
        "missing_referenced_paths": missing_paths,
        "validation_scope": "static_only_not_github_actions_runtime",
    }


def _parse_yaml(text: str) -> dict[str, Any] | None:
    try:
        payload = yaml.safe_load(text)
    except yaml.YAMLError:
        return None
    return payload if isinstance(payload, dict) else None


def _referenced_paths(text: str) -> list[str]:
    candidates = []
    for token in text.replace("\\\n", " ").split():
        normalized = token.strip("'\"")
        if normalized.startswith(("tests/", "scripts/", "configs/")):
            candidates.append(normalized)
    return sorted(set(candidates))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workflow", default=".github/workflows/ci.yml")
    return parser.parse_args()


if __name__ == "__main__":
    main()
