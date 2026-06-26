"""Plan external public benchmark ingestion from registry metadata."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from evoprior_aivc.data.public_benchmark_adapter import (
    GenericManifestOnlyAdapter,
    LocalFixtureBenchmarkAdapter,
)
from evoprior_aivc.evaluation.benchmark_registry import (
    BenchmarkRegistryRecord,
    load_benchmark_registry,
    summarize_registry,
)


def main() -> None:
    args = _parse_args()
    config = _load_yaml(Path(args.config))
    strict = bool(args.strict or config.get("strict", False))
    output_dir, summary = run_ingestion_planning(config, strict=strict)
    print(output_dir)
    if strict and summary["n_blocked"] > 0:
        raise SystemExit("strict mode failed: blocked benchmark records are present")


def run_ingestion_planning(
    config: dict[str, Any],
    *,
    strict: bool = False,
) -> tuple[Path, dict[str, int]]:
    """Create an auditable ingestion plan from a registry YAML."""
    if config.get("mode") != "public_benchmark_ingestion_plan":
        raise ValueError(f"unsupported mode: {config.get('mode')}")
    registry_path = Path(config["registry_path"])
    validation = load_benchmark_registry(registry_path)
    plans = [_plan_record(record, registry_path.parent) for record in validation.records]
    output_dir = _make_output_dir(config)
    output_dir.mkdir(parents=True, exist_ok=False)
    summary = _summary(validation.records, plans)
    _write_json(
        output_dir / "public_benchmark_ingestion_plan.json",
        {
            "registry_validation": validation.to_dict(),
            "plans": plans,
            "summary": summary,
            "strict": strict,
        },
    )
    table = _plan_table(validation.records, plans)
    table.to_csv(output_dir / "public_benchmark_ingestion_table.csv", index=False)
    (output_dir / "public_benchmark_ingestion_report.md").write_text(
        _report(config, summary, table),
        encoding="utf-8",
    )
    _write_yaml(output_dir / "resolved_config.yaml", config)
    _write_json(
        output_dir / "run_manifest.json",
        {
            "git_commit": _git_commit(),
            "experiment_id": config["experiment_id"],
            "registry_path": str(registry_path),
            "n_registered_benchmark_records": summary["n_records"],
            "n_blocked_records": summary["n_blocked"],
            "n_local_fixture_validated_records": summary["n_local_fixture_validated"],
            "claim_boundary": config.get("reporting", {}).get("claim_boundary"),
        },
    )
    if strict and summary["n_blocked"] > 0:
        raise ValueError("strict mode failed: blocked benchmark records are present")
    return output_dir, summary


def _plan_record(record: BenchmarkRegistryRecord, base_dir: Path) -> dict[str, Any]:
    if record.ingestion_status == "LOCAL_FIXTURE_VALIDATED":
        adapter = LocalFixtureBenchmarkAdapter(record.raw, base_dir=base_dir)
    else:
        adapter = GenericManifestOnlyAdapter(record.raw)
    plan = adapter.build_ingestion_plan()
    blocked_reasons = list(plan.blocked_reasons)
    blocked_reasons.extend(record.errors)
    return {
        **plan.to_dict(),
        "registry_valid": record.is_valid,
        "registry_errors": record.errors,
        "registry_warnings": record.warnings,
        "ingestion_status": record.ingestion_status,
        "evidence_status": record.evidence_status,
        "blocked_reasons": blocked_reasons,
    }


def _summary(records: list[BenchmarkRegistryRecord], plans: list[dict[str, Any]]) -> dict[str, int]:
    registry_summary = summarize_registry(
        type("ValidationProxy", (), {"records": records})()  # small structural proxy
    )
    n_blocked = sum(bool(plan["blocked_reasons"]) for plan in plans)
    n_ready = sum(
        not plan["blocked_reasons"]
        and plan.get("ingestion_status") in {"LOCAL_DATA_READY", "INGESTED"}
        for plan in plans
    )
    return {
        **registry_summary,
        "n_blocked": n_blocked,
        "n_ready_for_future_ingestion": n_ready,
    }


def _plan_table(
    records: list[BenchmarkRegistryRecord],
    plans: list[dict[str, Any]],
) -> pd.DataFrame:
    rows = []
    for record, plan in zip(records, plans, strict=True):
        rows.append(
            {
                "benchmark_id": record.normalized_benchmark_id,
                "dataset_name": record.dataset_name,
                "ingestion_status": record.ingestion_status,
                "evidence_status": record.evidence_status,
                "registry_valid": record.is_valid,
                "plan_blocked": bool(plan["blocked_reasons"]),
                "blocked_reasons": ";".join(plan["blocked_reasons"]),
                "split_policy": plan["split_policy"],
                "leakage_risks": ";".join(plan["leakage_risks"]),
                "model_trained": plan["model_trained"],
                "performance_claim": plan["performance_claim"],
            }
        )
    return pd.DataFrame(rows)


def _report(config: dict[str, Any], summary: dict[str, int], table: pd.DataFrame) -> str:
    metadata = table[table["ingestion_status"] == "REGISTERED_METADATA_ONLY"]
    fixtures = table[table["ingestion_status"] == "LOCAL_FIXTURE_VALIDATED"]
    blocked = table[table["plan_blocked"]]
    ready = table[~table["plan_blocked"]]
    lines = [
        f"# {config.get('reporting', {}).get('title', 'v0.11 Public Benchmark Ingestion Plan')}",
        "",
        "## Scope",
        "",
        "No model was trained. No performance claim was produced. No external data was committed.",
        "",
        "## Summary",
        "",
        _markdown_table(pd.DataFrame([summary])),
        "",
        "## Metadata-Only Registered Benchmarks",
        "",
        _markdown_table(metadata) if not metadata.empty else "No metadata-only records.",
        "",
        "## Local Fixture Validated Benchmarks",
        "",
        _markdown_table(fixtures) if not fixtures.empty else "No local fixture records.",
        "",
        "## Blocked Benchmarks",
        "",
        _markdown_table(blocked) if not blocked.empty else "No blocked records.",
        "",
        "## Ready For Future Ingestion",
        "",
        _markdown_table(ready) if not ready.empty else "No ready records.",
        "",
        "## Next Steps Before Benchmarking",
        "",
        "- Import legally usable local data outside git-tracked raw artifacts.",
        "- Validate schema and split policy without test-label leakage.",
        "- Run benchmark models only after ingestion status is ready.",
        "- Create v0.10 evidence records before making any performance statement.",
        "",
        "## Claim Boundary",
        "",
        config.get("reporting", {}).get(
            "claim_boundary",
            "Metadata registration is not benchmark evidence.",
        ),
        "",
    ]
    return "\n".join(lines)


def _make_output_dir(config: dict[str, Any]) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return Path(config["output_root"]) / config["output_prefix"] / timestamp


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


def _markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "No rows."
    columns = list(map(str, frame.columns))
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for _, row in frame.iterrows():
        lines.append("| " + " | ".join(str(row[column]) for column in frame.columns) + " |")
    return "\n".join(lines)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    main()
