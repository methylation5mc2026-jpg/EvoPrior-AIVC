"""Prepare or validate a configured real dataset file."""

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
    result = prepare_dataset(config, dry_run=args.dry_run)
    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to data config YAML.")
    parser.add_argument("--dry-run", action="store_true", help="Print the plan without downloading.")
    return parser.parse_args()


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


if __name__ == "__main__":
    main()

