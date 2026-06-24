"""Collect compact benchmark evidence from existing run directories."""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

DEFAULT_CLAIM_BOUNDARY = "No strong claim is supported by this record without manual review."


@dataclass
class BenchmarkEvidenceRecord:
    """One model/split evidence row derived from a benchmark run directory."""

    record_id: str
    run_dir: str
    dataset_id: str
    split_id: str
    model_id: str
    config_path: str | None = None
    metrics: dict[str, Any] = field(default_factory=dict)
    metrics_finite: bool = True
    coverage_manifest: dict[str, Any] | None = None
    component_audit: dict[str, Any] | None = None
    leakage_checks: dict[str, Any] | None = None
    claim_boundary: str = DEFAULT_CLAIM_BOUNDARY
    evidence_status: str = "missing"
    missing_artifacts: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    same_split_group: str | None = None
    lineage_comparison_status: str | None = None
    gene_prior_comparison_status: str | None = None
    shuffled_control_status: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable record."""
        return asdict(self)


def collect_run_evidence(
    run_dir: str | Path,
    *,
    config_path: str | None = None,
) -> list[BenchmarkEvidenceRecord]:
    """Collect evidence records for every model in a run directory."""
    run_path = Path(run_dir)
    manifest = _load_json(run_path / "run_manifest.json")
    config = _load_yaml(run_path / "resolved_config.yaml")
    metric_frame, metric_missing = _load_metric_frame(run_path)
    coverage, coverage_missing = _load_coverage(run_path, manifest)
    component, component_missing = _load_component_audit(run_path)
    leakage = _load_leakage_checks(run_path, manifest)
    claim_boundary = _claim_boundary(manifest, config)
    dataset_id = _dataset_id(run_path, manifest, config)

    if metric_frame.empty:
        return [
            BenchmarkEvidenceRecord(
                record_id=_record_id(dataset_id, "missing", "missing", run_path),
                run_dir=str(run_path),
                dataset_id=dataset_id,
                split_id="missing",
                model_id="missing",
                config_path=config_path,
                metrics_finite=False,
                coverage_manifest=coverage,
                component_audit=component,
                leakage_checks=leakage,
                claim_boundary=claim_boundary,
                evidence_status="missing",
                missing_artifacts=metric_missing + coverage_missing + component_missing,
                warnings=["no metrics file could be read"],
                same_split_group=f"{dataset_id}:missing",
            )
        ]

    records: list[BenchmarkEvidenceRecord] = []
    for key, group in metric_frame.groupby(["split_id", "model_id"], dropna=False):
        split_id, model_id = map(str, key)
        metrics, finite, warnings = _metrics_from_group(group)
        missing_artifacts = metric_missing + coverage_missing + component_missing
        status = _evidence_status(model_id, metrics, finite, component)
        records.append(
            BenchmarkEvidenceRecord(
                record_id=_record_id(dataset_id, split_id, model_id, run_path),
                run_dir=str(run_path),
                dataset_id=dataset_id,
                split_id=split_id,
                model_id=model_id,
                config_path=config_path,
                metrics=metrics,
                metrics_finite=finite,
                coverage_manifest=coverage,
                component_audit=component,
                leakage_checks=leakage,
                claim_boundary=claim_boundary,
                evidence_status=status,
                missing_artifacts=missing_artifacts,
                warnings=warnings,
                same_split_group=f"{dataset_id}:{split_id}",
            )
        )
    annotate_comparisons(records)
    return records


def annotate_comparisons(records: list[BenchmarkEvidenceRecord]) -> None:
    """Annotate lineage, no-gene-prior, and shuffled control comparison statuses."""
    for same_split_group, group_records in _group_by_same_split(records).items():
        del same_split_group
        by_model = {record.model_id: record for record in group_records}
        lineage_mae = _metric_mean(by_model.get("lineage_shrinkage"), "mae_delta")
        no_gene_mae = _metric_mean(by_model.get("evoprior_additive_no_gene_prior"), "mae_delta")
        shuffled_present = "evoprior_additive_shuffled_gene_prior" in by_model
        for record in group_records:
            record.lineage_comparison_status = _compare_with_reference(
                record,
                "lineage_shrinkage",
                lineage_mae,
            )
            record.shuffled_control_status = "present" if shuffled_present else "missing"
            record.gene_prior_comparison_status = _gene_prior_status(record, no_gene_mae)


def records_to_dataframe(records: list[BenchmarkEvidenceRecord]) -> pd.DataFrame:
    """Flatten records into a compact evidence table."""
    rows = []
    for record in records:
        row = {
            "record_id": record.record_id,
            "run_dir": record.run_dir,
            "dataset_id": record.dataset_id,
            "split_id": record.split_id,
            "model_id": record.model_id,
            "config_path": record.config_path,
            "metrics_finite": record.metrics_finite,
            "evidence_status": record.evidence_status,
            "claim_boundary": record.claim_boundary,
            "same_split_group": record.same_split_group,
            "lineage_comparison_status": record.lineage_comparison_status,
            "gene_prior_comparison_status": record.gene_prior_comparison_status,
            "shuffled_control_status": record.shuffled_control_status,
            "missing_artifacts": ";".join(record.missing_artifacts),
            "warnings": ";".join(record.warnings),
        }
        for metric, values in record.metrics.items():
            if isinstance(values, dict):
                row[f"{metric}_mean"] = values.get("mean")
                row[f"{metric}_n"] = values.get("n")
        rows.append(row)
    return pd.DataFrame(rows)


def write_evidence_outputs(
    records: list[BenchmarkEvidenceRecord],
    output_dir: str | Path,
    *,
    title: str,
) -> None:
    """Write JSON, CSV, and markdown benchmark evidence artifacts."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    payload = [record.to_dict() for record in records]
    (output_path / "benchmark_evidence.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    table = records_to_dataframe(records)
    table.to_csv(output_path / "benchmark_evidence_table.csv", index=False)
    (output_path / "benchmark_evidence_report.md").write_text(
        _evidence_report(title, records, table),
        encoding="utf-8",
    )


def _load_metric_frame(run_path: Path) -> tuple[pd.DataFrame, list[str]]:
    metric_summary = run_path / "metric_summary.csv"
    metrics = run_path / "metrics.csv"
    if metric_summary.exists():
        frame = pd.read_csv(metric_summary)
        return _normalize_metric_summary(frame), []
    if metrics.exists():
        frame = pd.read_csv(metrics)
        return _normalize_metrics(frame), ["metric_summary.csv"]
    return pd.DataFrame(), ["metric_summary.csv", "metrics.csv"]


def _normalize_metric_summary(frame: pd.DataFrame) -> pd.DataFrame:
    split_mode = frame.get("split_mode", pd.Series(["unknown"] * len(frame))).astype(str)
    split = frame.get("split", pd.Series(["unknown"] * len(frame))).astype(str)
    baseline = frame.get("baseline", frame.get("model_id", pd.Series(["unknown"] * len(frame))))
    normalized = frame.copy()
    normalized["split_id"] = split_mode + ":" + split
    normalized["model_id"] = baseline.astype(str)
    normalized["metric_name"] = frame.get("metric", pd.Series(["metric"] * len(frame))).astype(str)
    return normalized


def _normalize_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    split_mode = frame.get("split_mode", pd.Series(["unknown"] * len(frame))).astype(str)
    split = frame.get("split", pd.Series(["unknown"] * len(frame))).astype(str)
    baseline = frame.get("baseline", frame.get("model_id", pd.Series(["unknown"] * len(frame))))
    metric_columns = [
        column
        for column in frame.columns
        if column.endswith("_delta") or column in {"spearman_logfc", "pearson_delta"}
    ]
    rows = []
    for _, row in frame.iterrows():
        for metric in metric_columns:
            rows.append(
                {
                    "split_id": (
                        f"{row.get('split_mode', split_mode.iloc[0])}:"
                        f"{row.get('split', split.iloc[0])}"
                    ),
                    "model_id": str(row.get("baseline", row.get("model_id", baseline.iloc[0]))),
                    "metric_name": metric,
                    "mean": row.get(metric),
                    "n": 1,
                }
            )
    return pd.DataFrame(rows)


def _metrics_from_group(group: pd.DataFrame) -> tuple[dict[str, Any], bool, list[str]]:
    metrics: dict[str, Any] = {}
    finite = True
    warnings: list[str] = []
    for _, row in group.iterrows():
        metric_name = str(row["metric_name"])
        values = {
            "mean": _optional_float(row.get("mean")),
            "n": _optional_int(row.get("n")),
            "std": _optional_float(row.get("std")),
            "ci_low": _optional_float(row.get("ci_low")),
            "ci_high": _optional_float(row.get("ci_high")),
        }
        for value in values.values():
            if isinstance(value, float) and not math.isfinite(value):
                finite = False
                warnings.append(f"non-finite metric value for {metric_name}")
        metrics[metric_name] = values
    return metrics, finite, warnings


def _load_coverage(
    run_path: Path,
    manifest: dict[str, Any],
) -> tuple[dict[str, Any] | None, list[str]]:
    if "gene_prior_coverage" in manifest:
        return {"gene_prior_coverage": manifest["gene_prior_coverage"]}, []
    preparation = _load_json(run_path / "gene_prior_preparation.json")
    reports = sorted(run_path.glob("*coverage*.md"))
    if preparation or reports:
        return {
            "gene_prior_preparation": preparation or None,
            "coverage_reports": [path.name for path in reports],
        }, []
    return None, ["coverage_manifest"]


def _load_component_audit(run_path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    summary = _load_json(run_path / "component_audit_summary.json")
    report = run_path / "component_audit.md"
    if summary or report.exists():
        payload = summary or {}
        payload["component_audit_report"] = report.name if report.exists() else None
        return payload, []
    return None, ["component_audit"]


def _load_leakage_checks(run_path: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "split_manifest_present": (run_path / "split_manifest.csv").exists(),
        "heldout_eligibility_present": (run_path / "heldout_cell_type_eligibility.csv").exists(),
        "control_usage": manifest.get("control_usage"),
    }


def _claim_boundary(manifest: dict[str, Any], config: dict[str, Any]) -> str:
    if isinstance(manifest.get("claim_boundary"), str):
        return manifest["claim_boundary"]
    reporting = config.get("reporting", {}) if isinstance(config, dict) else {}
    if isinstance(reporting.get("claim_boundary"), str):
        return reporting["claim_boundary"]
    return DEFAULT_CLAIM_BOUNDARY


def _dataset_id(run_path: Path, manifest: dict[str, Any], config: dict[str, Any]) -> str:
    for source in (manifest, config):
        value = source.get("dataset_id") if isinstance(source, dict) else None
        if isinstance(value, str) and value:
            return value
    if run_path.parent.name:
        return run_path.parent.name
    return "unknown_dataset"


def _evidence_status(
    model_id: str,
    metrics: dict[str, Any],
    finite: bool,
    component: dict[str, Any] | None,
) -> str:
    if not finite:
        return "invalid"
    if not metrics:
        return "missing"
    if model_id.startswith("evoprior_additive") and component is None:
        return "weak"
    return "pass"


def _compare_with_reference(
    record: BenchmarkEvidenceRecord,
    reference_model: str,
    reference_mae: float | None,
) -> str:
    if record.model_id == reference_model:
        return "self"
    current_mae = _metric_mean(record, "mae_delta")
    if current_mae is None or reference_mae is None:
        return f"missing_{reference_model}"
    if current_mae < reference_mae:
        return f"beats_{reference_model}"
    if math.isclose(current_mae, reference_mae, rel_tol=1e-9, abs_tol=1e-12):
        return f"matches_{reference_model}"
    return f"trails_{reference_model}"


def _gene_prior_status(record: BenchmarkEvidenceRecord, no_gene_mae: float | None) -> str:
    if (
        "gene_prior" not in record.model_id
        or "no_gene_prior" in record.model_id
        or "gene_prior_disabled" in record.model_id
    ):
        return "not_applicable"
    current_mae = _metric_mean(record, "mae_delta")
    if current_mae is None or no_gene_mae is None:
        return "missing_no_gene_prior"
    if current_mae < no_gene_mae:
        return "beats_no_gene_prior"
    if math.isclose(current_mae, no_gene_mae, rel_tol=1e-9, abs_tol=1e-12):
        return "matches_no_gene_prior"
    return "trails_no_gene_prior"


def _metric_mean(record: BenchmarkEvidenceRecord | None, metric: str) -> float | None:
    if record is None:
        return None
    values = record.metrics.get(metric)
    if not isinstance(values, dict):
        return None
    value = values.get("mean")
    return value if isinstance(value, float) and math.isfinite(value) else None


def _group_by_same_split(
    records: list[BenchmarkEvidenceRecord],
) -> dict[str, list[BenchmarkEvidenceRecord]]:
    grouped: dict[str, list[BenchmarkEvidenceRecord]] = {}
    for record in records:
        key = record.same_split_group or f"{record.dataset_id}:{record.split_id}"
        grouped.setdefault(key, []).append(record)
    return grouped


def _record_id(dataset_id: str, split_id: str, model_id: str, run_path: Path) -> str:
    safe_split = split_id.replace(":", "_").replace("/", "_")
    safe_model = model_id.replace("/", "_")
    return f"{dataset_id}::{safe_split}::{safe_model}::{run_path.name}"


def _optional_float(value: Any) -> float | None:
    if value is None or value == "" or pd.isna(value):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _optional_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    return payload if isinstance(payload, dict) else {}


def _evidence_report(
    title: str,
    records: list[BenchmarkEvidenceRecord],
    table: pd.DataFrame,
) -> str:
    statuses = table["evidence_status"].value_counts().to_dict() if not table.empty else {}
    comparable = sorted(set(table.get("same_split_group", pd.Series(dtype=str)).dropna()))
    gene_prior_statuses = sorted(
        set(table.get("gene_prior_comparison_status", pd.Series(dtype=str)).dropna())
    )
    comparison_lines = _comparison_scope_lines(records)
    component_lines = _component_audit_lines(records)
    lines = [
        f"# {title}",
        "",
        "## Scope",
        "",
        "v0.10 aligns existing benchmark evidence. It does not add model capacity or prove SOTA.",
        "",
        "## Status Counts",
        "",
        _markdown_table(pd.DataFrame([statuses])) if statuses else "No records.",
        "",
        "## Same-Split Groups",
        "",
        "\n".join(f"- `{item}`" for item in comparable) if comparable else "No comparable groups.",
        "",
        "## Models Comparable Within Same Split",
        "",
        "\n".join(comparison_lines) if comparison_lines else "No within-split comparisons.",
        "",
        "## Smoke Or Integration-Only Results",
        "",
        "Synthetic and compatibility records validate plumbing only unless a real benchmark split "
        "and matching controls are documented.",
        "",
        "## Gene-Prior Negative-Control Status",
        "",
        "\n".join(f"- `{item}`" for item in gene_prior_statuses)
        if gene_prior_statuses
        else "No gene-prior comparison available.",
        "",
        "## Component Audit Status",
        "",
        "\n".join(component_lines) if component_lines else "No component audit available.",
        "",
        "## Evolutionary/Conservation Claim Status",
        "",
        "Not established by this evidence table. HGNC metadata is not orthology, conservation "
        "score, or gene age.",
        "",
        "## Claim Boundary",
        "",
        "External public benchmark alignment remains blocked until external splits are imported.",
        "HGNC metadata does not establish true evolutionary/conservation-prior benefit.",
        "",
        "## Evidence Table Preview",
        "",
        _markdown_table(table.head(20)) if not table.empty else "No rows.",
        "",
    ]
    return "\n".join(lines)


def _comparison_scope_lines(records: list[BenchmarkEvidenceRecord]) -> list[str]:
    lines = []
    for key, group in sorted(_group_by_same_split(records).items()):
        models = ", ".join(sorted({record.model_id for record in group}))
        lines.append(f"- `{key}`: {models}")
    return lines


def _component_audit_lines(records: list[BenchmarkEvidenceRecord]) -> list[str]:
    lines = []
    seen: set[str] = set()
    for record in records:
        if record.component_audit is None or record.run_dir in seen:
            continue
        seen.add(record.run_dir)
        collapsed = record.component_audit.get("gene_prior_collapsed")
        mostly_lineage = record.component_audit.get("mostly_lineage")
        lines.append(
            f"- `{record.run_dir}`: gene_prior_collapsed={collapsed}, "
            f"mostly_lineage={mostly_lineage}"
        )
    return lines


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
