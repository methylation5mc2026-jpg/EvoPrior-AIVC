"""Diagnose official GEARS/cell-gears environment readiness."""

from __future__ import annotations

import importlib.metadata
import importlib.util
import json
import os
import platform
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PackageProbe:
    name: str
    module: str
    importable: bool
    version: str
    location: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "module": self.module,
            "importable": self.importable,
            "version": self.version,
            "location": self.location,
        }


def main() -> None:
    run_dir = _make_run_dir()
    run_dir.mkdir(parents=True, exist_ok=False)
    payload = build_diagnostic_payload()
    payload["run_dir"] = str(run_dir)
    (run_dir / "diagnostic_report.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (run_dir / "diagnostic_report.md").write_text(_markdown_report(payload), encoding="utf-8")
    print(run_dir)
    print(payload["status"])


def build_diagnostic_payload() -> dict[str, Any]:
    probes = [
        probe_package("torch", "torch"),
        probe_package("torch-geometric", "torch_geometric"),
        probe_package("cell-gears", "gears"),
        probe_package("gears", "gears"),
    ]
    venv_probe = probe_venv_gears()
    wrapper = run_wrapper_dry_run(use_venv=venv_probe["gears_import_ok"])
    status = classify_official_gears_status(
        main_probes=[probe.to_dict() for probe in probes],
        venv_probe=venv_probe,
        wrapper_result=wrapper,
    )
    return {
        "status": status["status"],
        "blocker_category": status["blocker_category"],
        "recommended_next_step": status["recommended_next_step"],
        "docker_wsl_next_action": docker_wsl_next_action(),
        "relation_to_prior_blockers": (
            "v0.14 documented missing dependencies, v0.18 documented import_ok_run_blocked "
            "inside .venv_gears, and v0.20 provides a Docker/WSL environment route without "
            "claiming official GEARS execution."
        ),
        "python": {
            "executable": sys.executable,
            "version": sys.version,
            "platform": platform.platform(),
        },
        "main_environment": [probe.to_dict() for probe in probes],
        "venv_gears": venv_probe,
        "wrapper_dry_run": wrapper,
        "exact_error": exact_error(venv_probe=venv_probe, wrapper_result=wrapper),
    }


def probe_package(distribution: str, module: str) -> PackageProbe:
    spec = importlib.util.find_spec(module)
    importable = spec is not None
    location = str(spec.origin) if spec and spec.origin else "not_importable"
    try:
        version = importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        version = "not_installed"
    return PackageProbe(
        name=distribution,
        module=module,
        importable=importable,
        version=version,
        location=location,
    )


def probe_venv_gears() -> dict[str, Any]:
    python = Path(".venv_gears") / "Scripts" / "python.exe"
    if not python.exists():
        return {
            "exists": False,
            "python": str(python),
            "torch_import_ok": False,
            "torch_geometric_import_ok": False,
            "gears_import_ok": False,
            "stdout": "",
            "stderr": "missing .venv_gears",
        }
    code = (
        "import torch; print('torch=' + torch.__version__); "
        "import torch_geometric; print('torch_geometric=ok'); "
        "import gears; print('gears=ok')"
    )
    env = dict(os.environ)
    env["MPLCONFIGDIR"] = ".tmp_mpl_gears"
    result = subprocess.run(
        [str(python), "-c", code],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    return {
        "exists": True,
        "python": str(python),
        "returncode": result.returncode,
        "torch_import_ok": "torch=" in stdout,
        "torch_geometric_import_ok": "torch_geometric=ok" in stdout,
        "gears_import_ok": "gears=ok" in stdout,
        "stdout": stdout,
        "stderr": stderr,
    }


def run_wrapper_dry_run(*, use_venv: bool) -> dict[str, Any]:
    python = (
        str(Path(".venv_gears") / "Scripts" / "python.exe")
        if use_venv
        else sys.executable
    )
    command = [
        python,
        "scripts/run_official_gears_wrapper.py",
        "--config",
        "configs/experiment/gears_norman_v014_official_wrapper.yaml",
        "--dry-run",
    ]
    env = dict(os.environ)
    env["PYTHONPATH"] = "src"
    env["MPLCONFIGDIR"] = ".tmp_mpl_gears"
    result = subprocess.run(command, check=False, capture_output=True, text=True, env=env)
    return {
        "command": " ".join(command),
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def classify_official_gears_status(
    *,
    main_probes: list[dict[str, Any]],
    venv_probe: dict[str, Any],
    wrapper_result: dict[str, Any],
) -> dict[str, str]:
    main_imports = {item["module"]: bool(item["importable"]) for item in main_probes}
    if not main_imports.get("torch", False) or not main_imports.get("gears", False):
        if venv_probe.get("gears_import_ok") and wrapper_result.get("returncode") == 0:
            return {
                "status": "import_ok_run_blocked",
                "blocker_category": "api_mismatch",
                "recommended_next_step": (
                    "Implement a real official GEARS train/evaluate wrapper or use a "
                    "Docker/WSL environment with pinned GEARS scripts and official split files."
                ),
            }
        return {
            "status": "dependency_blocked",
            "blocker_category": "import_missing",
            "recommended_next_step": (
                "Create an isolated environment or Docker/WSL image with pinned torch, "
                "torch-geometric, and cell-gears versions."
            ),
        }
    if not main_imports.get("torch_geometric", False):
        return {
            "status": "dependency_blocked",
            "blocker_category": "pyg_missing",
            "recommended_next_step": "Install a torch-compatible torch-geometric build.",
        }
    if wrapper_result.get("returncode") == 0:
        return {
            "status": "import_ok_run_blocked",
            "blocker_category": "api_mismatch",
            "recommended_next_step": (
                "Replace feasibility-only wrapper with official training/evaluation."
            ),
        }
    return {
        "status": "dependency_blocked",
        "blocker_category": "runtime_error",
        "recommended_next_step": (
            "Inspect diagnostic stderr and pin the failing runtime dependency."
        ),
    }


def docker_wsl_next_action() -> dict[str, str]:
    return {
        "docker_build": "docker build -f docker/Dockerfile.gears -t evoprior-gears-env .",
        "docker_import_check": (
            "docker run --rm evoprior-gears-env "
            "python -c \"import torch; import torch_geometric; import gears; print('ok')\""
        ),
        "wsl_note": (
            "Use WSL2 or Docker for a clean Linux-like PyTorch/PyG stack before "
            "implementing official GEARS train/evaluate alignment."
        ),
    }


def exact_error(*, venv_probe: dict[str, Any], wrapper_result: dict[str, Any]) -> str:
    candidates = [
        str(wrapper_result.get("stderr", "")).strip(),
        str(venv_probe.get("stderr", "")).strip(),
    ]
    for candidate in candidates:
        if candidate:
            return candidate.splitlines()[-1]
    return "no stderr captured"


def _markdown_report(payload: dict[str, Any]) -> str:
    lines = [
        "# v0.20 Official GEARS Diagnostic Report",
        "",
        f"- Status: `{payload['status']}`",
        f"- Blocker category: `{payload['blocker_category']}`",
        f"- Recommended next step: {payload['recommended_next_step']}",
        f"- Exact error: `{payload['exact_error']}`",
        f"- Relation to prior blockers: {payload['relation_to_prior_blockers']}",
        "",
        "## Main Environment",
        "",
        "| package | module | importable | version | location |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in payload["main_environment"]:
        lines.append(
            f"| {item['name']} | {item['module']} | {item['importable']} | "
            f"{item['version']} | {item['location']} |"
        )
    lines.extend(
        [
            "",
            "## .venv_gears",
            "",
            "```json",
            json.dumps(payload["venv_gears"], indent=2, ensure_ascii=False),
            "```",
            "",
            "## Wrapper Dry-Run",
            "",
            "```json",
            json.dumps(payload["wrapper_dry_run"], indent=2, ensure_ascii=False),
            "```",
            "",
            "## Docker / WSL Next Action",
            "",
            "```json",
            json.dumps(payload["docker_wsl_next_action"], indent=2, ensure_ascii=False),
            "```",
            "",
            "## Claim Boundary",
            "",
            "This is a diagnostic artifact, not an official GEARS result.",
            "",
        ]
    )
    return "\n".join(lines)


def _make_run_dir() -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return Path("outputs/runs/v0.20-official-gears-diagnostics") / timestamp


if __name__ == "__main__":
    main()
