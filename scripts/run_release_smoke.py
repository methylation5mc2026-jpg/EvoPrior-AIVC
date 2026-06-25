"""Run a lightweight v0.19 release smoke check."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from evoprior_aivc.baselines import (
    DeltaDataset,
    ResidualComboConfig,
    ResidualComboCorrectionBaseline,
)


@dataclass(frozen=True)
class SmokeCheck:
    check_id: str
    status: str
    detail: str
    critical: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "status": self.status,
            "detail": self.detail,
            "critical": self.critical,
        }


def main() -> None:
    args = _parse_args()
    config = _load_yaml(Path(args.config))
    run_dir = _make_run_dir(config)
    run_dir.mkdir(parents=True, exist_ok=False)
    checks = run_release_smoke(config)
    payload = {
        "experiment_id": config["experiment_id"],
        "status": "pass" if _critical_pass(checks) else "fail",
        "checks": [check.to_dict() for check in checks],
    }
    (run_dir / "smoke_report.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (run_dir / "smoke_report.md").write_text(_markdown_report(payload), encoding="utf-8")
    print(run_dir)
    print(payload["status"])
    if payload["status"] != "pass":
        raise SystemExit(1)


def run_release_smoke(config: dict[str, Any]) -> list[SmokeCheck]:
    checks = [
        _check_import(config["package"]["import_name"]),
        _check_paths("required_docs", config["release"]["required_docs"]),
        _check_paths("required_configs", config["release"]["required_configs"]),
        _check_paths("required_scripts", config["release"]["required_scripts"]),
        _check_norman_data(config["data"]),
        _check_v017_output(config["release"]["v017_output"]),
        _check_tiny_residual_baseline(),
        _check_pytest_subset(config["release"].get("pytest_subset", [])),
    ]
    return checks


def _check_import(import_name: str) -> SmokeCheck:
    try:
        module = importlib.import_module(import_name)
    except Exception as exc:  # pragma: no cover - detail path
        return SmokeCheck("python_import", "fail", repr(exc))
    version = getattr(module, "__version__", "unknown")
    return SmokeCheck("python_import", "pass", f"{import_name} version={version}")


def _check_paths(check_id: str, paths: list[str]) -> SmokeCheck:
    missing = [path for path in paths if not Path(path).exists()]
    status = "pass" if not missing else "fail"
    return SmokeCheck(check_id, status, f"missing={missing}")


def _check_norman_data(data_config: dict[str, Any]) -> SmokeCheck:
    path = Path(data_config["norman_path"])
    if not path.exists():
        return SmokeCheck(
            "norman_data",
            "warn",
            (
                f"data missing at {path}; run "
                "python scripts/prepare_gears_norman.py --config "
                "configs/data/gears_norman_v013.yaml --dry-run"
            ),
            critical=False,
        )
    observed = _md5(path)
    expected = data_config["checksum_md5"]
    status = "pass" if observed == expected else "fail"
    return SmokeCheck("norman_data", status, f"md5={observed}; expected={expected}")


def _check_v017_output(output_path: str) -> SmokeCheck:
    path = Path(output_path)
    if not path.exists():
        return SmokeCheck(
            "v017_output",
            "warn",
            f"output missing at {path}; rerun v0.17 command if local metrics are needed",
            critical=False,
        )
    required = ["aggregate_metrics.csv", "leakage_stress_checks.csv", "ablation_summary.csv"]
    missing = [name for name in required if not (path / name).exists()]
    return SmokeCheck("v017_output", "pass" if not missing else "fail", f"missing={missing}")


def _check_tiny_residual_baseline() -> SmokeCheck:
    try:
        dataset = _tiny_delta_dataset()
        model = ResidualComboCorrectionBaseline(
            ResidualComboConfig(
                residual_model="none",
                residual_scale=0.0,
                weighted_ridge_alpha=0.0,
            )
        ).fit(dataset)
        predicted = model.predict_delta(dataset)
        finite = bool(np.isfinite(predicted.to_numpy()).all())
    except Exception as exc:  # pragma: no cover - detail path
        return SmokeCheck("tiny_residual_baseline", "fail", repr(exc))
    return SmokeCheck("tiny_residual_baseline", "pass" if finite else "fail", f"finite={finite}")


def _check_pytest_subset(paths: list[str]) -> SmokeCheck:
    if not paths:
        return SmokeCheck("pytest_subset", "warn", "no pytest subset configured", critical=False)
    command = [
        "python",
        "-m",
        "pytest",
        "-p",
        "no:cacheprovider",
        "--basetemp",
        ".tmp_pytest_v19_smoke",
        *paths,
    ]
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    detail = (result.stdout + result.stderr).strip().splitlines()[-3:]
    return SmokeCheck(
        "pytest_subset",
        "pass" if result.returncode == 0 else "fail",
        " | ".join(detail),
    )


def _tiny_delta_dataset() -> DeltaDataset:
    metadata = pd.DataFrame(
        {
            "perturbation": ["A", "B", "A+B"],
            "perturbation_type": ["single", "single", "combo"],
            "perturbation_genes": ["A", "B", "A;B"],
            "cell_type": ["K562", "K562", "K562"],
            "split_class": ["single_seen", "single_seen", "seen2"],
        },
        index=["A", "B", "A+B"],
    )
    gene_names = ["gene_0", "gene_1"]
    delta = pd.DataFrame(
        [[1.0, 0.0], [0.0, 1.0], [1.2, 1.1]],
        index=metadata.index,
        columns=gene_names,
    )
    control = pd.DataFrame(0.0, index=metadata.index, columns=delta.columns)
    return DeltaDataset(
        group_ids=tuple(metadata.index),
        metadata=metadata,
        control_expression=control,
        observed_post_expression=delta,
        observed_delta=delta,
    )


def _critical_pass(checks: list[SmokeCheck]) -> bool:
    return all(check.status == "pass" for check in checks if check.critical)


def _md5(path: Path) -> str:
    digest = hashlib.md5()  # noqa: S324 - checksum matches public data manifest
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _markdown_report(payload: dict[str, Any]) -> str:
    lines = [
        "# v0.19 Release Smoke Report",
        "",
        f"- Status: `{payload['status']}`",
        "",
        "| check | status | critical | detail |",
        "| --- | --- | --- | --- |",
    ]
    for check in payload["checks"]:
        lines.append(
            f"| {check['check_id']} | {check['status']} | {check['critical']} | "
            f"{check['detail']} |"
        )
    lines.append("")
    return "\n".join(lines)


def _make_run_dir(config: dict[str, Any]) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return Path(config["output_root"]) / config["output_prefix"] / timestamp


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
