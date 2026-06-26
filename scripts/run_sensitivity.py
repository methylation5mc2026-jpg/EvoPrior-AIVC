"""Run a compact v0.4 preprocessing sensitivity audit."""

from __future__ import annotations

import argparse
import copy
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from evoprior_aivc.baselines import (
    ControlMeanBaseline,
    HierarchicalAdditiveBaseline,
    PerturbationMeanDeltaBaselineV2,
    RidgeCVBaseline,
    build_delta_dataset,
)
from evoprior_aivc.data.download import prepare_dataset
from evoprior_aivc.data.preprocess import preprocess_adata
from evoprior_aivc.data.pseudobulk import aggregate_pseudobulk
from evoprior_aivc.data.real_loader import load_real_dataset
from evoprior_aivc.data.splits import assign_group_holdout_split, assign_random_group_split
from evoprior_aivc.evaluation.evaluator import evaluate_delta_predictions, subset_delta_dataset
from evoprior_aivc.evaluation.leakage_checks import assert_holdout_split_has_no_train_leakage


def main() -> None:
    args = _parse_args()
    sensitivity_config = _load_yaml(Path(args.config))
    base_config = _load_yaml(Path(sensitivity_config["base_config"]))
    run_dir = _make_run_dir(sensitivity_config, base_config)
    run_dir.mkdir(parents=True, exist_ok=False)
    _write_yaml(run_dir / "resolved_config.yaml", sensitivity_config)

    prepare_dataset(base_config["data"], dry_run=False)
    raw_adata, _ = load_real_dataset(base_config["data"])

    rows: list[dict[str, object]] = []
    for top_n in sensitivity_config["matrix"]["top_n_genes"]:
        for min_cells in sensitivity_config["matrix"]["min_cells_per_group"]:
            for split_mode in sensitivity_config["matrix"]["split_modes"]:
                setting = {
                    "top_n_genes": int(top_n),
                    "min_cells_per_group": int(min_cells),
                    "split_mode": split_mode,
                }
                try:
                    rows.extend(
                        _run_setting(
                            raw_adata,
                            base_config=base_config,
                            sensitivity_config=sensitivity_config,
                            setting=setting,
                        )
                    )
                except Exception as exc:  # noqa: BLE001 - report and continue matrix audit
                    rows.append({**setting, "status": "skipped", "reason": str(exc)})

    results = pd.DataFrame(rows)
    results.to_csv(run_dir / "sensitivity_results.csv", index=False)
    summary = _summarize(results)
    summary.to_csv(run_dir / "sensitivity_summary.csv", index=False)
    (run_dir / "git_commit.txt").write_text(_git_commit(), encoding="utf-8")
    _write_report(run_dir / "report.md", results, summary)
    print(run_dir)


def _run_setting(
    raw_adata,
    *,
    base_config: dict[str, Any],
    sensitivity_config: dict[str, Any],
    setting: dict[str, object],
) -> list[dict[str, object]]:
    config = copy.deepcopy(base_config)
    config["preprocessing"]["max_genes"] = int(setting["top_n_genes"])
    config["pseudobulk"]["min_cells"] = int(setting["min_cells_per_group"])
    adata = preprocess_adata(raw_adata, config)
    expression, metadata = aggregate_pseudobulk(
        adata,
        groupby=tuple(config["pseudobulk"]["groupby"]),
        layer=config["pseudobulk"].get("layer"),
        min_cells=int(config["pseudobulk"]["min_cells"]),
        aggregation=config["pseudobulk"]["aggregation"],
    )
    dataset = build_delta_dataset(
        expression,
        metadata,
        control_label=config["delta"]["control_label"],
        match_columns=tuple(config["delta"]["match_columns"]),
        fallback=config["delta"].get("control_fallback", "raise"),
    )
    if setting["split_mode"] == "random_group":
        split = assign_random_group_split(
            dataset.metadata,
            val_fraction=0.2,
            test_fraction=0.2,
            seed=int(sensitivity_config["seed"]),
        )
    elif setting["split_mode"] == "heldout_pdl1":
        split = assign_group_holdout_split(
            dataset.metadata,
            holdout={"perturbation": ["pdl1"]},
            val_fraction=0.2,
            seed=int(sensitivity_config["seed"]),
        )
        assert_holdout_split_has_no_train_leakage(
            dataset.metadata,
            split,
            holdout={"perturbation": ["pdl1"]},
        )
    else:
        raise ValueError(f"unsupported split mode: {setting['split_mode']}")

    train = subset_delta_dataset(dataset, split == "train")
    query = subset_delta_dataset(dataset, split == "test")
    rows: list[dict[str, object]] = []
    for baseline in _baselines(sensitivity_config["baselines"]):
        baseline.fit(train)
        prediction = baseline.predict_delta(query)
        metrics = evaluate_delta_predictions(query, prediction)
        rows.append(
            {
                **setting,
                "status": "ok",
                "reason": "",
                "baseline": baseline.name,
                "n_pseudobulk_groups": expression.shape[0],
                "n_test_examples": len(query.group_ids),
                **metrics,
            }
        )
    return rows


def _baselines(names: list[str]):
    for name in names:
        if name == "control_mean":
            yield ControlMeanBaseline()
        elif name == "perturbation_mean_delta_v2":
            yield PerturbationMeanDeltaBaselineV2(fallback="global")
        elif name == "hierarchical_additive":
            yield HierarchicalAdditiveBaseline(alpha=5.0)
        elif name == "ridge_cv":
            yield RidgeCVBaseline(alphas=(0.1, 1.0, 10.0))
        else:
            raise ValueError(f"unsupported sensitivity baseline: {name}")


def _summarize(results: pd.DataFrame) -> pd.DataFrame:
    ok = results[results["status"] == "ok"]
    if ok.empty:
        return pd.DataFrame()
    return (
        ok.groupby(["split_mode", "baseline"], dropna=False)
        .agg(
            n_settings=("mae_delta", "count"),
            mae_min=("mae_delta", "min"),
            mae_max=("mae_delta", "max"),
            mae_mean=("mae_delta", "mean"),
            mse_mean=("mse_delta", "mean"),
        )
        .reset_index()
    )


def _write_report(path: Path, results: pd.DataFrame, summary: pd.DataFrame) -> None:
    lines = [
        "# v0.4 Preprocessing Sensitivity Audit",
        "",
        "This is a compact engineering audit, not hyperparameter optimization.",
        "",
        "## Summary",
        "",
        summary.to_string(index=False) if not summary.empty else "No successful settings.",
        "",
        "## Skipped Settings",
        "",
        results[results["status"] != "ok"].to_string(index=False)
        if not results[results["status"] != "ok"].empty
        else "No skipped settings.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to sensitivity config.")
    return parser.parse_args()


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _write_yaml(path: Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=False, allow_unicode=True)


def _make_run_dir(config: dict[str, Any], base_config: dict[str, Any]) -> Path:
    dataset_id = base_config["data"]["dataset"]["dataset_id"]
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return Path(config["output_root"]) / config["output_prefix"] / dataset_id / timestamp


def _git_commit() -> str:
    result = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=False)
    return result.stdout.strip() if result.returncode == 0 else "unknown"


if __name__ == "__main__":
    main()

