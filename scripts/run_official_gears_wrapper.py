"""Run or block the optional official GEARS wrapper for v0.14."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

import yaml

from evoprior_aivc.external.gears_wrapper import (
    probe_gears_feasibility,
    run_official_gears_or_block,
)


def main() -> None:
    args = _parse_args()
    config = _load_yaml(Path(args.config))
    preflight = probe_gears_feasibility(
        list(config.get("official_wrapper", {}).get("known_install_blockers", []))
    )
    if args.dry_run or preflight.decision != "run_official_wrapper_now":
        output_prefix = config["output_prefix_dry_run"]
    else:
        output_prefix = config["output_prefix"]
    run_dir = _make_run_dir(config, output_prefix=output_prefix)
    feasibility = run_official_gears_or_block(
        config=config,
        run_dir=run_dir,
        dry_run=args.dry_run,
    )
    print(run_dir)
    print(feasibility.decision)


def _make_run_dir(config: dict, *, output_prefix: str) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return (
        Path(config["output_root"])
        / output_prefix
        / config["benchmark_id"]
        / timestamp
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    return payload if isinstance(payload, dict) else {}


if __name__ == "__main__":
    main()
