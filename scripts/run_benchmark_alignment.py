"""Run v0.10 benchmark evidence alignment over existing run directories."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from evoprior_aivc.evaluation.benchmark_evidence import (
    BenchmarkEvidenceRecord,
    collect_run_evidence,
    write_evidence_outputs,
)


def main() -> None:
    args = _parse_args()
    config = _load_yaml(Path(args.config))
    run_dir = run_alignment(config)
    print(run_dir)


def run_alignment(config: dict[str, Any]) -> Path:
    if config.get("mode") != "benchmark_alignment":
        raise ValueError(f"unsupported mode: {config.get('mode')}")
    output_dir = _make_output_dir(config)
    output_dir.mkdir(parents=True, exist_ok=False)
    records: list[BenchmarkEvidenceRecord] = []
    for run in config.get("runs", []):
        source_run_dir = Path(run["run_dir"])
        run_records = collect_run_evidence(
            source_run_dir,
            config_path=run.get("config_path"),
        )
        role = run.get("evidence_role")
        for record in run_records:
            if role:
                record.warnings.append(f"evidence_role={role}")
        records.extend(run_records)
    title = config.get("reporting", {}).get("title", "v0.10 Benchmark Evidence")
    write_evidence_outputs(records, output_dir, title=title)
    _write_yaml(output_dir / "resolved_config.yaml", config)
    _write_json(
        output_dir / "run_manifest.json",
        {
            "git_commit": _git_commit(),
            "experiment_id": config["experiment_id"],
            "dataset_id": config["dataset_id"],
            "n_source_runs": len(config.get("runs", [])),
            "n_evidence_records": len(records),
            "claim_boundary": config.get("reporting", {}).get("claim_boundary"),
        },
    )
    return output_dir


def _make_output_dir(config: dict[str, Any]) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return Path(config["output_root"]) / config["output_prefix"] / config["dataset_id"] / timestamp


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    return payload if isinstance(payload, dict) else {}


def _write_yaml(path: Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=False, allow_unicode=True)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _git_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    main()
