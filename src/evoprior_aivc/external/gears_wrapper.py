"""Optional wrapper utilities for official GEARS/cell-gears execution."""

from __future__ import annotations

import importlib.metadata
import importlib.util
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class GearsFeasibility:
    """Import/package feasibility summary for official GEARS wrappers."""

    gears_available: bool
    cell_gears_available: bool
    torch_available: bool
    torch_geometric_available: bool
    versions: dict[str, str]
    blockers: list[str]
    decision: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable summary."""
        return {
            "gears_available": self.gears_available,
            "cell_gears_available": self.cell_gears_available,
            "torch_available": self.torch_available,
            "torch_geometric_available": self.torch_geometric_available,
            "versions": self.versions,
            "blockers": self.blockers,
            "decision": self.decision,
        }


def probe_gears_feasibility(extra_blockers: list[str] | None = None) -> GearsFeasibility:
    """Probe optional GEARS dependencies without importing heavy modules."""
    gears_available = _module_available("gears")
    cell_gears_available = _distribution_available("cell-gears")
    torch_available = _module_available("torch")
    torch_geometric_available = _module_available("torch_geometric")
    versions = {
        name: _distribution_version(name)
        for name in ("cell-gears", "gears", "torch", "torch-geometric")
    }
    blockers: list[str] = []
    if not gears_available:
        blockers.append("Python module `gears` is not importable.")
    if not cell_gears_available:
        blockers.append("Distribution `cell-gears` is not installed.")
    if not torch_available:
        blockers.append("Python module `torch` is not importable.")
    if not torch_geometric_available:
        blockers.append("Python module `torch_geometric` is not importable.")
    blockers.extend(extra_blockers or [])
    if gears_available and torch_available:
        decision = "run_official_wrapper_now"
    elif cell_gears_available or torch_available:
        decision = "inspect_near_official_adapter"
    else:
        decision = "document_blocker"
    return GearsFeasibility(
        gears_available=gears_available,
        cell_gears_available=cell_gears_available,
        torch_available=torch_available,
        torch_geometric_available=torch_geometric_available,
        versions=versions,
        blockers=blockers,
        decision=decision,
    )


def run_official_gears_or_block(
    *,
    config: dict[str, Any],
    run_dir: Path,
    dry_run: bool,
) -> GearsFeasibility:
    """Write an official GEARS blocker report unless the wrapper is feasible.

    v0.14 intentionally does not implement a neural GEARS model. If the official
    dependency stack is unavailable, this function records the exact blocker and
    exits cleanly through the caller.
    """
    run_dir.mkdir(parents=True, exist_ok=False)
    feasibility = probe_gears_feasibility(
        list(config.get("official_wrapper", {}).get("known_install_blockers", []))
    )
    payload = {
        "dry_run": dry_run,
        "config": config,
        "feasibility": feasibility.to_dict(),
        "command": (
            "python scripts/run_official_gears_wrapper.py --config "
            "configs/experiment/gears_norman_v014_official_wrapper.yaml"
            + (" --dry-run" if dry_run else "")
        ),
        "git_commit": _git_commit(),
    }
    (run_dir / "wrapper_feasibility.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    if feasibility.decision != "run_official_wrapper_now":
        _write_blocker_report(run_dir / "blocker_report.md", payload)
        return feasibility
    _write_blocker_report(
        run_dir / "blocker_report.md",
        {
            **payload,
            "note": (
                "Official GEARS dependencies appear importable, but v0.14 does not "
                "train a neural GEARS model automatically. Runbook steps are in docs."
            ),
        },
    )
    return feasibility


def _write_blocker_report(path: Path, payload: dict[str, Any]) -> None:
    feasibility = payload["feasibility"]
    lines = [
        "# v0.14 Official GEARS Wrapper Blocker Report",
        "",
        f"- Dry run: `{payload['dry_run']}`",
        f"- Decision: `{feasibility['decision']}`",
        f"- Command: `{payload['command']}`",
        f"- Git commit: `{payload['git_commit']}`",
        "",
        "## Package Versions",
        "",
        *_dict_lines(feasibility["versions"]),
        "",
        "## Blockers",
        "",
        *[f"- {item}" for item in feasibility["blockers"]],
        "",
        "## Claim Boundary",
        "",
        "This is an official-wrapper feasibility artifact, not an official GEARS run.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def _module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _distribution_available(name: str) -> bool:
    try:
        importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return False
    return True


def _distribution_version(name: str) -> str:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return "not_installed"


def _dict_lines(values: dict[str, str]) -> list[str]:
    return [f"- `{key}`: `{value}`" for key, value in values.items()]


def _git_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"

