"""Run the v0.15 fast neural-style Norman baseline."""

from __future__ import annotations

import argparse
import json
import subprocess
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from evoprior_aivc.baselines import (
    FastComboMLPConfig,
    FastComboMLPPCA,
    SingleEffectAdditiveComboBaseline,
    WeightedComboAdditiveBaseline,
    build_delta_dataset,
)
from evoprior_aivc.data.download import prepare_dataset
from evoprior_aivc.data.gears_norman_adapter import (
    load_gears_norman_dataset,
    write_gears_norman_schema_report,
)
from evoprior_aivc.data.gears_splits import (
    assign_gears_compatible_combo_split,
    write_gears_split_report,
)
from evoprior_aivc.data.preprocess import preprocess_adata
from evoprior_aivc.data.pseudobulk import aggregate_pseudobulk
from evoprior_aivc.evaluation.benchmark_evidence import collect_run_evidence, write_evidence_outputs
from evoprior_aivc.evaluation.evaluator import evaluate_delta_predictions, subset_delta_dataset
from evoprior_aivc.evaluation.gears_metrics import (
    de_rows_for_dataset,
    per_class_metrics,
    per_perturbation_metrics,
)
from evoprior_aivc.evaluation.leakage_checks import assert_no_target_derived_features


def main() -> None:
    args = _parse_args()
    config = _load_yaml(Path(args.config))
    config["config_path"] = args.config
    if args.smoke:
        _apply_smoke_overrides(config)
    data_payload = _load_yaml(Path(config["data_config"]))
    data_config = data_payload["data"]
    preparation = prepare_dataset(data_config)
    run_dir = _make_run_dir(config)
    data_report_dir = Path("outputs/data_reports") / config["benchmark_id"] / run_dir.name
    run_dir.mkdir(parents=True, exist_ok=False)
    data_report_dir.mkdir(parents=True, exist_ok=True)
    _write_yaml(run_dir / "resolved_config.yaml", config)
    _write_yaml(run_dir / "resolved_data_config.yaml", data_payload)

    adata, schema_report = load_gears_norman_dataset(data_config, path=preparation.path)
    write_gears_norman_schema_report(schema_report, data_report_dir)
    write_gears_norman_schema_report(schema_report, run_dir)
    adata = preprocess_adata(adata, config)
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
        fallback=config["delta"].get("control_fallback", "global"),
    )
    assert_no_target_derived_features(config["features"]["allowed_feature_columns"])
    split, split_manifest, split_audit = assign_gears_compatible_combo_split(
        dataset.metadata,
        seed=int(config["split"]["seed"]),
        seen_gene_fraction=float(config["split"]["seen_gene_fraction"]),
        test_combo_fraction=float(config["split"]["test_combo_fraction"]),
        random_combo_fraction=float(config["split"].get("random_combo_fraction", 0.0)),
        val_fraction=float(config["split"]["val_fraction"]),
        min_test_combos_per_class=int(config["split"]["min_test_combos_per_class"]),
    )
    split_class_by_group = split_manifest.set_index("group_id")["split_class"]
    dataset.metadata["split_class"] = dataset.metadata.index.astype(str).map(split_class_by_group)
    split_manifest.to_csv(run_dir / "split_manifest.csv", index=False)
    split_manifest.to_csv(data_report_dir / "split_manifest.csv", index=False)
    write_gears_split_report(
        run_dir / "split_report.md",
        split_manifest=split_manifest,
        audit=split_audit,
    )
    write_gears_split_report(
        data_report_dir / "split_report.md",
        split_manifest=split_manifest,
        audit=split_audit,
    )

    metrics, per_pert, per_class, de_rows, model_rows = _evaluate(
        config,
        dataset,
        split,
        run_dir=run_dir,
    )
    seed_summary = _metric_seed_summary(
        metrics,
        metric_columns=tuple(config["evaluation"]["metric_columns"]),
    )
    per_class_summary = _summarize_per_class(per_class)
    de_summary = _summarize_de(de_rows)

    metrics.to_csv(run_dir / "metrics.csv", index=False)
    metrics.to_json(run_dir / "metrics.json", orient="records", indent=2)
    seed_summary.to_csv(run_dir / "seed_metric_summary.csv", index=False)
    per_pert.to_csv(run_dir / "per_perturbation_metrics.csv", index=False)
    per_class.to_csv(run_dir / "per_class_metrics.csv", index=False)
    per_class_summary.to_csv(run_dir / "per_class_metric_summary.csv", index=False)
    de_rows.to_csv(run_dir / "de_metrics.csv", index=False)
    de_summary.to_csv(run_dir / "de_summary.csv", index=False)
    pd.DataFrame(model_rows).to_csv(run_dir / "model_seed_manifest.csv", index=False)
    _write_json(run_dir / "dataset_preparation.json", preparation.to_dict())
    _write_json(run_dir / "schema_report.json", schema_report.__dict__)
    _write_json(run_dir / "split_leakage_audit.json", split_audit)
    command_config_path = config.get(
        "config_path",
        "configs/experiment/gears_norman_v015_fast_neural.yaml",
    )
    _write_json(
        run_dir / "run_manifest.json",
        {
            "git_commit": _git_commit(),
            "experiment_id": config["experiment_id"],
            "benchmark_id": config["benchmark_id"],
            "dataset_id": config["dataset_id"],
            "command": (
                "python scripts/run_fast_neural_norman.py --config "
                f"{command_config_path}"
            ),
            "data_source": config["benchmark"]["source"],
            "data_checksum": data_config["dataset"]["checksum"],
            "split_definition": config["benchmark"]["split_definition"],
            "metric_script": "src/evoprior_aivc/evaluation/gears_metrics.py",
            "alignment_status": config["benchmark"]["official_alignment_status"],
            "claim_boundary": config["reporting"]["claim_boundary"],
        },
    )
    _write_report(
        run_dir,
        config=config,
        seed_summary=seed_summary,
        per_class_summary=per_class_summary,
        de_summary=de_summary,
        split_audit=split_audit,
        data_report_dir=data_report_dir,
        preparation=preparation.to_dict(),
    )
    records = collect_run_evidence(run_dir, config_path=args.config)
    write_evidence_outputs(records, run_dir, title="v0.15 Fast Neural Norman Evidence")
    print(run_dir)


def _evaluate(config: dict[str, Any], dataset, split: pd.Series, *, run_dir: Path):
    metric_rows: list[dict[str, Any]] = []
    per_perturbation_frames: list[pd.DataFrame] = []
    per_class_frames: list[pd.DataFrame] = []
    de_frames: list[pd.DataFrame] = []
    model_rows: list[dict[str, Any]] = []
    train = subset_delta_dataset(dataset, split == "train")
    for baseline in _reference_baselines(config.get("reference_baselines", [])):
        baseline.fit(train)
        _evaluate_model(
            baseline,
            dataset,
            split,
            metric_rows=metric_rows,
            per_perturbation_frames=per_perturbation_frames,
            per_class_frames=per_class_frames,
            de_frames=de_frames,
            de_ks=tuple(config["evaluation"]["de_ks"]),
            seed=None,
            run_kind="reference_recomputed",
        )
    for seed in config["model"]["seeds"]:
        seed = int(seed)
        model = FastComboMLPPCA(_mlp_config(config["model"], seed=seed))
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            model.fit(train)
        warning_text = [str(item.message) for item in caught]
        manifest = model.manifest()
        manifest["fit_warnings"] = warning_text
        manifest_path = run_dir / f"model_manifest_seed_{seed}.json"
        curve_path = run_dir / f"training_curve_seed_{seed}.csv"
        _write_json(manifest_path, manifest)
        model.training_curve().to_csv(curve_path, index=False)
        model_rows.append(
            {
                "seed": seed,
                "model_manifest": str(manifest_path),
                "training_curve": str(curve_path),
                "n_iter": manifest["fit_status"]["n_iter"],
                "final_loss": manifest["fit_status"]["final_loss"],
                "n_warnings": len(warning_text),
            }
        )
        _evaluate_model(
            model,
            dataset,
            split,
            metric_rows=metric_rows,
            per_perturbation_frames=per_perturbation_frames,
            per_class_frames=per_class_frames,
            de_frames=de_frames,
            de_ks=tuple(config["evaluation"]["de_ks"]),
            seed=seed,
            run_kind="trained_neural_sklearn",
        )
    return (
        pd.DataFrame(metric_rows),
        _concat_frames(per_perturbation_frames),
        _concat_frames(per_class_frames),
        _concat_frames(de_frames),
        model_rows,
    )


def _evaluate_model(
    baseline,
    dataset,
    split: pd.Series,
    *,
    metric_rows: list[dict[str, Any]],
    per_perturbation_frames: list[pd.DataFrame],
    per_class_frames: list[pd.DataFrame],
    de_frames: list[pd.DataFrame],
    de_ks: tuple[int, ...],
    seed: int | None,
    run_kind: str,
) -> None:
    for split_label in ("val", "test"):
        mask = split == split_label
        if not mask.any():
            continue
        query = subset_delta_dataset(dataset, mask)
        predicted = baseline.predict_delta(query)
        metrics = evaluate_delta_predictions(query, predicted)
        metric_rows.append(
            {
                "split": split_label,
                "baseline": baseline.name,
                "run_kind": run_kind,
                "seed": seed,
                "n_examples": len(query.group_ids),
                **metrics,
            }
        )
        per_pert = per_perturbation_metrics(query, predicted)
        per_pert.insert(0, "seed", seed)
        per_pert.insert(0, "run_kind", run_kind)
        per_pert.insert(0, "baseline", baseline.name)
        per_pert.insert(0, "split", split_label)
        per_perturbation_frames.append(per_pert)
        per_cls = per_class_metrics(query, predicted)
        per_cls.insert(0, "seed", seed)
        per_cls.insert(0, "run_kind", run_kind)
        per_cls.insert(0, "baseline", baseline.name)
        per_cls.insert(0, "split", split_label)
        per_class_frames.append(per_cls)
        de_frame = pd.DataFrame(de_rows_for_dataset(query, predicted, ks=de_ks))
        de_frame.insert(0, "seed", seed)
        de_frame.insert(0, "run_kind", run_kind)
        de_frame.insert(0, "baseline", baseline.name)
        de_frame.insert(0, "split", split_label)
        de_frames.append(de_frame)


def _reference_baselines(configs: list[dict[str, Any]]):
    for config in configs:
        name = config["name"]
        if name == "single_effect_additive_combo":
            yield SingleEffectAdditiveComboBaseline(
                missing_single_fallback=config.get(
                    "missing_single_fallback",
                    "global_single_mean",
                )
            )
        elif name == "weighted_combo_additive":
            yield WeightedComboAdditiveBaseline(
                ridge_alpha=float(config.get("ridge_alpha", 1.0)),
                missing_single_fallback=config.get(
                    "missing_single_fallback",
                    "global_single_mean",
                ),
            )
        else:
            raise ValueError(f"unsupported reference baseline: {name}")


def _mlp_config(payload: dict[str, Any], *, seed: int) -> FastComboMLPConfig:
    return FastComboMLPConfig(
        pca_components=int(payload.get("pca_components", 32)),
        hidden_layer_sizes=tuple(int(value) for value in payload.get("hidden_layer_sizes", [64])),
        alpha=float(payload.get("alpha", 0.0001)),
        learning_rate_init=float(payload.get("learning_rate_init", 0.001)),
        max_iter=int(payload.get("max_iter", 250)),
        tol=float(payload.get("tol", 0.0001)),
        early_stopping=bool(payload.get("early_stopping", True)),
        validation_fraction=float(payload.get("validation_fraction", 0.15)),
        n_iter_no_change=int(payload.get("n_iter_no_change", 20)),
        random_state=seed,
        include_cell_type=bool(payload.get("include_cell_type", True)),
        include_perturbation_type=bool(payload.get("include_perturbation_type", True)),
    )


def _metric_seed_summary(metrics: pd.DataFrame, *, metric_columns: tuple[str, ...]) -> pd.DataFrame:
    if metrics.empty:
        return metrics
    rows = []
    group_columns = ["split", "baseline", "run_kind"]
    for values, group in metrics.groupby(group_columns, dropna=False):
        split, baseline, run_kind = values
        row = {
            "split": split,
            "baseline": baseline,
            "run_kind": run_kind,
            "n_rows": int(len(group)),
            "n_seeds": int(group["seed"].nunique(dropna=True)),
            "n_examples": int(group["n_examples"].max()),
        }
        for column in metric_columns:
            series = pd.to_numeric(group[column], errors="coerce").dropna()
            row[f"{column}_mean"] = float(series.mean()) if not series.empty else None
            row[f"{column}_std"] = float(series.std(ddof=0)) if len(series) > 1 else 0.0
        rows.append(row)
    return pd.DataFrame(rows)


def _summarize_per_class(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame
    metric_columns = ["mae_delta", "mse_delta", "pearson_delta", "spearman_logfc"]
    return (
        frame.groupby(
            ["split", "baseline", "run_kind", "group_column", "group_value"],
            dropna=False,
        )[metric_columns]
        .mean(numeric_only=True)
        .reset_index()
    )


def _summarize_de(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame
    metric_columns = [
        column
        for column in frame.columns
        if column.startswith("top_") or column == "spearman_gene_rank"
    ]
    return (
        frame.groupby(
            ["split", "baseline", "run_kind", "perturbation_type", "split_class"],
            dropna=False,
        )[metric_columns]
        .mean(numeric_only=True)
        .reset_index()
    )


def _write_report(
    run_dir: Path,
    *,
    config: dict[str, Any],
    seed_summary: pd.DataFrame,
    per_class_summary: pd.DataFrame,
    de_summary: pd.DataFrame,
    split_audit: dict[str, Any],
    data_report_dir: Path,
    preparation: dict[str, Any],
) -> None:
    reference_frame = pd.DataFrame(config["comparison_reference"]["rows"])
    lines = [
        "# v0.15 Fast Neural Norman Baseline",
        "",
        "## Executive Summary",
        "",
        (
            "A lightweight sklearn MLPRegressor baseline was trained on PCA-compressed "
            "delta-expression targets for the public Norman/scPerturb GEARS-compatible "
            "internal split."
        ),
        "",
        "## Benchmark And Alignment",
        "",
        f"- Status: `{config['benchmark']['official_alignment_status']}`",
        f"- Notes: {config['benchmark']['official_alignment_notes']}",
        "- Official GEARS model/split/metrics: not imported.",
        "",
        "## Data Source And Checksum",
        "",
        f"- Source: {config['benchmark']['source']}",
        f"- Local path: `{preparation['path']}`",
        f"- Checksum status: `{preparation['checksum_status']}`",
        "",
        "## Schema And Split",
        "",
        f"- Schema report path: `{data_report_dir / 'schema_report.md'}`",
        f"- Split definition: {config['benchmark']['split_definition']}",
        f"- Leakage audit passed: `{split_audit['overall_pass']}`",
        f"- Test combo leakage: `{split_audit['leaked_test_combos']}`",
        "",
        "## Model",
        "",
        f"- Name: `{config['model']['name']}`",
        f"- Backend: `{config['model']['backend']}`",
        f"- Seeds: `{config['model']['seeds']}`",
        "- Features: perturbation genes, perturbation type, and cell type from train metadata.",
        (
            "- Target: PCA-compressed train delta expression; validation/test deltas "
            "are never used for fitting."
        ),
        "",
        "## Main Result Table",
        "",
        _markdown_table(seed_summary),
        "",
        "## v0.14 Historical Reference",
        "",
        f"- Reference output: `{config['comparison_reference']['v014_output_dir']}`",
        f"- Note: {config['comparison_reference']['note']}",
        "",
        _markdown_table(reference_frame),
        "",
        "## Per-Class Breakdown",
        "",
        _markdown_table(per_class_summary),
        "",
        "## DE20/DE50 Recovery",
        "",
        _markdown_table(de_summary),
        "",
        "## Failure Cases",
        "",
        (
            "Inspect `per_perturbation_metrics.csv`, `per_class_metrics.csv`, "
            "and seed-specific training curves."
        ),
        "",
        "## What Can Be Externally Claimed",
        "",
        (
            "We executed a reproducible fast sklearn MLP/PCA neural-style baseline on "
            "the public Norman/scPerturb GEARS-compatible internal split with documented "
            "data, split, metrics, and seed repeats."
        ),
        "",
        "## What Cannot Be Claimed",
        "",
        "- No SOTA claim.",
        "- No official GEARS or leaderboard-comparable claim.",
        "- No biological discovery claim.",
        "- No general neural-model superiority claim.",
        "",
        "## Next Steps",
        "",
        "- Install or containerize official GEARS dependencies for a true wrapper run.",
        "- Strengthen model features only through validation-set decisions.",
        (
            "- Preserve the v0.14/v0.15 claim boundary until official split and "
            "metric parity are proven."
        ),
        "",
        "## Claim Boundary",
        "",
        config["reporting"]["claim_boundary"],
        "",
    ]
    (run_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")


def _concat_frames(frames: list[pd.DataFrame]) -> pd.DataFrame:
    nonempty = [frame for frame in frames if not frame.empty]
    if not nonempty:
        return pd.DataFrame()
    columns = list(dict.fromkeys(column for frame in nonempty for column in frame.columns))
    rows = [record for frame in nonempty for record in frame.to_dict("records")]
    return pd.DataFrame.from_records(rows, columns=columns)


def _markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "No rows."
    columns = list(map(str, frame.columns))
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for _, row in frame.iterrows():
        cells = [_format_cell(row[column]) for column in frame.columns]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def _format_cell(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def _make_run_dir(config: dict[str, Any]) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return (
        Path(config["output_root"])
        / config["output_prefix"]
        / config["benchmark_id"]
        / timestamp
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--smoke", action="store_true")
    return parser.parse_args()


def _apply_smoke_overrides(config: dict[str, Any]) -> None:
    config["experiment_id"] = f"{config['experiment_id']}-smoke"
    config["output_prefix"] = f"{config['output_prefix']}-smoke"
    seeds = list(config["model"].get("seeds", []))
    if seeds:
        config["model"]["seeds"] = seeds[:1]
    config["model"]["max_iter"] = min(int(config["model"].get("max_iter", 250)), 50)
    config["reporting"]["claim_boundary"] = (
        config["reporting"]["claim_boundary"] + " Smoke mode is compatibility-only."
    )


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


if __name__ == "__main__":
    main()
