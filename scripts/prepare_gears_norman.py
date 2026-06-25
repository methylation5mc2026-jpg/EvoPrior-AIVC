"""Prepare or dry-run the v0.13 GEARS/Norman benchmark data."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from evoprior_aivc.data.download import prepare_dataset


def main() -> None:
    args = _parse_args()
    config = _load_yaml(Path(args.config))
    data_config = config["data"]
    result = prepare_dataset(data_config, dry_run=args.dry_run)
    report_dir = _make_report_dir(config)
    report_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "benchmark_id": config["benchmark"]["benchmark_id"],
        "dry_run": args.dry_run,
        "source_mode": config["benchmark"]["source_mode"],
        "official_or_compatible": config["benchmark"]["official_or_compatible"],
        "result": result.to_dict(),
    }
    (report_dir / "data_access_report.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (report_dir / "data_access_report.md").write_text(
        _markdown_report(config, payload),
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _markdown_report(config: dict[str, Any], payload: dict[str, Any]) -> str:
    result = payload["result"]
    blocker = "none" if result["status"] in {"ready", "dry_run"} else result["message"]
    lines = [
        "# v0.13 GEARS/Norman Data Access Report",
        "",
        f"- Benchmark ID: `{payload['benchmark_id']}`",
        f"- Source mode: `{payload['source_mode']}`",
        f"- Alignment: `{payload['official_or_compatible']}`",
        f"- Local path: `{result['path']}`",
        f"- Status: `{result['status']}`",
        f"- Downloaded: `{result['downloaded']}`",
        f"- Checksum status: `{result['checksum_status']}`",
        f"- Source: {config['benchmark']['source_url_or_reference']}",
        f"- Expected size bytes: {config['benchmark']['expected_local_size_bytes']}",
        f"- Unresolved blockers: {blocker}",
        "",
        "Raw data must not be committed.",
        "",
    ]
    return "\n".join(lines)


def _make_report_dir(config: dict[str, Any]) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return Path("outputs/data_reports") / config["benchmark"]["benchmark_id"] / timestamp


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    return payload if isinstance(payload, dict) else {}


if __name__ == "__main__":
    main()
