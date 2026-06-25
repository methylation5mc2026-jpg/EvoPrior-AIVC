"""Leakage stress checks for Norman residual validation runs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

SPLIT_CLASS_TOKENS: tuple[str, ...] = (
    "seen0",
    "seen1",
    "seen2",
    "random_combo",
    "single_unseen",
    "single_seen",
)


@dataclass(frozen=True)
class LeakageStressResult:
    """One leakage stress check result."""

    check_id: str
    passed: bool
    severity: str
    detail: str


def run_norman_leakage_stress_checks(
    *,
    split_manifest: pd.DataFrame,
    config: dict[str, Any],
    selected_metrics: dict[str, float],
    shuffled_target_metrics: dict[str, float] | None = None,
    shuffled_feature_metrics: dict[str, float] | None = None,
) -> list[LeakageStressResult]:
    """Run fixed leakage stress checks for the v0.17 Norman package."""
    results = [
        _check_no_test_combo_in_train_like(split_manifest),
        _check_disjoint_split_groups(split_manifest),
        _check_selection_protocol(config),
        _check_perturbation_labels_do_not_encode_split_class(split_manifest),
        _check_split_manifest_classes(split_manifest),
        _check_feature_policy(config),
    ]
    if shuffled_target_metrics is not None:
        results.append(
            _check_negative_control_degrades(
                check_id="shuffled_target_control_degrades",
                selected_metrics=selected_metrics,
                control_metrics=shuffled_target_metrics,
            )
        )
    if shuffled_feature_metrics is not None:
        results.append(
            _check_negative_control_degrades(
                check_id="shuffled_feature_control_degrades",
                selected_metrics=selected_metrics,
                control_metrics=shuffled_feature_metrics,
            )
        )
    return results


def stress_results_to_frame(results: list[LeakageStressResult]) -> pd.DataFrame:
    """Convert stress results to a stable table."""
    return pd.DataFrame(
        [
            {
                "check_id": result.check_id,
                "passed": bool(result.passed),
                "severity": result.severity,
                "detail": result.detail,
            }
            for result in results
        ]
    )


def all_critical_checks_pass(results: list[LeakageStressResult]) -> bool:
    """Return whether all critical checks passed."""
    return all(result.passed for result in results if result.severity == "critical")


def write_leakage_stress_report(
    path: str | Path,
    *,
    results: list[LeakageStressResult],
    title: str = "v0.17 Leakage Stress Report",
) -> None:
    """Write a markdown leakage stress report."""
    frame = stress_results_to_frame(results)
    lines = [
        f"# {title}",
        "",
        f"- Critical checks passed: `{all_critical_checks_pass(results)}`",
        f"- Checks: `{len(results)}`",
        "",
        _markdown_table(frame),
        "",
    ]
    Path(path).write_text("\n".join(lines), encoding="utf-8")


def _check_no_test_combo_in_train_like(split_manifest: pd.DataFrame) -> LeakageStressResult:
    test_combos = set(
        split_manifest.loc[
            (split_manifest["split"] == "test")
            & (split_manifest["perturbation_type"] == "combo"),
            "perturbation",
        ].astype(str)
    )
    train_like = split_manifest[split_manifest["split"].isin(["train", "val"])]
    leaked = sorted(set(train_like["perturbation"].astype(str)).intersection(test_combos))
    return LeakageStressResult(
        check_id="no_test_combo_in_train_or_val",
        passed=not leaked,
        severity="critical",
        detail=f"leaked_test_combos={leaked}",
    )


def _check_disjoint_split_groups(split_manifest: pd.DataFrame) -> LeakageStressResult:
    groups_by_split = {
        split: set(group["group_id"].astype(str))
        for split, group in split_manifest.groupby("split", dropna=False)
    }
    overlaps: list[str] = []
    for left_name, left in groups_by_split.items():
        for right_name, right in groups_by_split.items():
            if str(left_name) >= str(right_name):
                continue
            overlap = sorted(left.intersection(right))
            if overlap:
                overlaps.append(f"{left_name}/{right_name}:{overlap[:5]}")
    return LeakageStressResult(
        check_id="train_val_test_group_ids_disjoint",
        passed=not overlaps,
        severity="critical",
        detail="; ".join(overlaps) if overlaps else "no overlaps",
    )


def _check_selection_protocol(config: dict[str, Any]) -> LeakageStressResult:
    selection = config.get("selection", {})
    uses_validation = selection.get("split") == "val"
    metric = str(selection.get("metric", ""))
    not_test_metric = "test" not in metric.lower()
    return LeakageStressResult(
        check_id="selection_protocol_uses_validation_not_test",
        passed=uses_validation and not_test_metric,
        severity="critical",
        detail=f"selection_split={selection.get('split')}; metric={selection.get('metric')}",
    )


def _check_perturbation_labels_do_not_encode_split_class(
    split_manifest: pd.DataFrame,
) -> LeakageStressResult:
    labels = split_manifest["perturbation"].astype(str).str.lower()
    leaks = sorted(
        {
            token
            for token in SPLIT_CLASS_TOKENS
            if labels.str.contains(token.lower(), regex=False).any()
        }
    )
    return LeakageStressResult(
        check_id="perturbation_label_does_not_encode_split_class",
        passed=not leaks,
        severity="critical",
        detail=f"split_class_tokens_in_perturbation_labels={leaks}",
    )


def _check_split_manifest_classes(split_manifest: pd.DataFrame) -> LeakageStressResult:
    observed = set(split_manifest["split"].astype(str))
    required = {"train", "val", "test"}
    missing = sorted(required.difference(observed))
    class_values = set(split_manifest["split_class"].astype(str))
    expected_any = {"seen0", "seen1", "seen2", "random_combo"}
    has_combo_class = bool(class_values.intersection(expected_any))
    return LeakageStressResult(
        check_id="split_manifest_has_expected_sets_and_classes",
        passed=not missing and has_combo_class,
        severity="critical",
        detail=f"missing_splits={missing}; split_classes={sorted(class_values)}",
    )


def _check_feature_policy(config: dict[str, Any]) -> LeakageStressResult:
    policy = str(config.get("features", {}).get("leakage_policy", "")).lower()
    ok = "train" in policy and "validation" in policy and "test" in policy
    return LeakageStressResult(
        check_id="feature_policy_documents_train_val_test_use",
        passed=ok,
        severity="critical",
        detail=policy or "missing feature leakage policy",
    )


def _check_negative_control_degrades(
    *,
    check_id: str,
    selected_metrics: dict[str, float],
    control_metrics: dict[str, float],
) -> LeakageStressResult:
    selected_mae = float(selected_metrics["mae_delta"])
    control_mae = float(control_metrics["mae_delta"])
    selected_mse = float(selected_metrics["mse_delta"])
    control_mse = float(control_metrics["mse_delta"])
    passed = control_mae > selected_mae and control_mse > selected_mse
    return LeakageStressResult(
        check_id=check_id,
        passed=passed,
        severity="critical",
        detail=(
            f"selected_mae={selected_mae:.6g}; control_mae={control_mae:.6g}; "
            f"selected_mse={selected_mse:.6g}; control_mse={control_mse:.6g}"
        ),
    )


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
