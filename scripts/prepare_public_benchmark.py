"""Prepare or dry-run a public benchmark dataset for v0.12."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from evoprior_aivc.data.download import prepare_dataset


def main() -> None:
    args = _parse_args()
    config = _load_yaml(Path(args.config))
    data_config = config.get("data", config)
    benchmark = config.get("benchmark", {})
    result = prepare_dataset(data_config, dry_run=args.dry_run)
    payload = {
        "benchmark_id": benchmark.get("benchmark_id", data_config["dataset"]["dataset_id"]),
        "dry_run": args.dry_run,
        "result": result.to_dict(),
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))


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
