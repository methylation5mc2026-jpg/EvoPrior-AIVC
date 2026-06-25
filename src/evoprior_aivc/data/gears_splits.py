"""GEARS-compatible combo perturbation split helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from evoprior_aivc.data.gears_norman_adapter import perturbation_genes_from_encoded


def assign_gears_compatible_combo_split(
    metadata: pd.DataFrame,
    *,
    seed: int = 0,
    seen_gene_fraction: float = 0.7,
    test_combo_fraction: float = 0.25,
    val_fraction: float = 0.1,
    min_test_combos_per_class: int = 1,
) -> tuple[pd.Series, pd.DataFrame, dict[str, Any]]:
    """Assign GEARS-compatible internal split labels for single/combo perturbations."""
    _validate_metadata(metadata)
    rng = np.random.default_rng(seed)
    perturbations = _perturbation_table(metadata)
    singles = perturbations[perturbations["perturbation_type"] == "single"].copy()
    combos = perturbations[perturbations["perturbation_type"] == "combo"].copy()
    if singles.empty or combos.empty:
        raise ValueError("GEARS-compatible combo split requires singles and combos")

    single_genes = sorted({genes[0] for genes in singles["genes"] if len(genes) == 1})
    n_seen = max(1, int(round(len(single_genes) * seen_gene_fraction)))
    n_seen = min(n_seen, len(single_genes))
    seen_genes = set(rng.choice(np.asarray(single_genes, dtype=object), size=n_seen, replace=False))

    perturbations["split_class"] = perturbations.apply(
        lambda row: _split_class(row["genes"], row["perturbation_type"], seen_genes),
        axis=1,
    )
    test_combos = _select_test_combos(
        perturbations,
        rng=rng,
        test_combo_fraction=test_combo_fraction,
        min_test_combos_per_class=min_test_combos_per_class,
    )
    labels_by_perturbation = {
        str(row.perturbation): "train" for row in perturbations.itertuples(index=False)
    }
    for perturbation in test_combos:
        labels_by_perturbation[str(perturbation)] = "test"
    for row in perturbations.itertuples(index=False):
        if row.perturbation_type == "single" and row.genes and row.genes[0] not in seen_genes:
            labels_by_perturbation[str(row.perturbation)] = "test"

    train_like = [
        perturbation
        for perturbation, label in labels_by_perturbation.items()
        if label == "train" and perturbation != "control"
    ]
    n_val = int(np.floor(len(train_like) * val_fraction))
    if n_val > 0:
        val = rng.choice(np.asarray(train_like, dtype=object), size=n_val, replace=False)
        for perturbation in val:
            labels_by_perturbation[str(perturbation)] = "val"

    split = metadata["perturbation"].astype(str).map(labels_by_perturbation).fillna("train")
    class_by_perturbation = perturbations.set_index("perturbation")["split_class"].to_dict()
    manifest = metadata.copy()
    manifest.insert(0, "group_id", metadata.index.astype(str))
    manifest.insert(1, "split", split.astype(str).to_numpy())
    manifest["split_class"] = manifest["perturbation"].astype(str).map(class_by_perturbation)
    manifest["split_class"] = manifest["split_class"].fillna("control")
    audit = leakage_audit(manifest)
    return split.astype("category"), manifest.reset_index(drop=True), audit


def leakage_audit(split_manifest: pd.DataFrame) -> dict[str, Any]:
    """Audit that held-out combo perturbations are absent from train/val."""
    required = {"split", "perturbation", "perturbation_type"}
    missing = required.difference(split_manifest.columns)
    if missing:
        raise KeyError(f"split manifest missing columns: {', '.join(sorted(missing))}")
    test_combos = set(
        split_manifest.loc[
            (split_manifest["split"] == "test")
            & (split_manifest["perturbation_type"] == "combo"),
            "perturbation",
        ].astype(str)
    )
    train_like = split_manifest[split_manifest["split"].isin(["train", "val"])]
    leaked = sorted(set(train_like["perturbation"].astype(str)).intersection(test_combos))
    counts = (
        split_manifest.groupby(["split", "perturbation_type"], dropna=False)
        .size()
        .reset_index(name="n_groups")
        .to_dict(orient="records")
    )
    class_counts = (
        split_manifest.groupby(["split", "split_class"], dropna=False)
        .size()
        .reset_index(name="n_groups")
        .to_dict(orient="records")
    )
    return {
        "overall_pass": not leaked,
        "leaked_test_combos": leaked,
        "n_test_combos": len(test_combos),
        "counts": counts,
        "class_counts": class_counts,
        "control_usage": (
            "matched control profiles are allowed input state; post-perturbation "
            "test deltas are not used for training features"
        ),
        "official_gears_split": False,
        "alignment_status": "GEARS-compatible/internal",
    }


def write_gears_split_report(
    path: Path,
    *,
    split_manifest: pd.DataFrame,
    audit: dict[str, Any],
) -> None:
    """Write a markdown split report."""
    path.parent.mkdir(parents=True, exist_ok=True)
    split_counts = (
        split_manifest.groupby(["split", "perturbation_type"], dropna=False)
        .size()
        .reset_index(name="n_groups")
    )
    class_counts = (
        split_manifest.groupby(["split", "split_class"], dropna=False)
        .size()
        .reset_index(name="n_groups")
    )
    train_perturbations = _perturbations_by_split(split_manifest, "train")
    val_perturbations = _perturbations_by_split(split_manifest, "val")
    test_perturbations = _perturbations_by_split(split_manifest, "test")
    lines = [
        "# v0.13 GEARS-Compatible Split Report",
        "",
        "- Split mode: `gears_compatible_combo`",
        "- Alignment: `GEARS-compatible/internal`; official GEARS split file not imported",
        f"- Leakage audit pass: `{audit['overall_pass']}`",
        f"- Test combo leakage: `{audit['leaked_test_combos']}`",
        "",
        "## Counts By Split And Perturbation Type",
        "",
        _markdown_table(split_counts),
        "",
        "## Counts By Split Class",
        "",
        _markdown_table(class_counts),
        "",
        "## Perturbations",
        "",
        f"- Train perturbations: {len(train_perturbations)}",
        f"- Val perturbations: {len(val_perturbations)}",
        f"- Test perturbations: {len(test_perturbations)}",
        "",
        "## Leakage Audit",
        "",
        "No test combo target may appear in train or validation rows.",
        "",
        "```json",
        json.dumps(audit, indent=2, ensure_ascii=False),
        "```",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    (path.parent / "split_leakage_audit.json").write_text(
        json.dumps(audit, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _validate_metadata(metadata: pd.DataFrame) -> None:
    required = {"perturbation", "perturbation_type", "perturbation_genes"}
    missing = required.difference(metadata.columns)
    if missing:
        raise KeyError(f"metadata missing columns: {', '.join(sorted(missing))}")


def _perturbation_table(metadata: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for perturbation, group in metadata.groupby("perturbation", sort=True, observed=True):
        perturbation_type = str(group["perturbation_type"].iloc[0])
        encoded = group["perturbation_genes"].iloc[0]
        genes = perturbation_genes_from_encoded(encoded)
        rows.append(
            {
                "perturbation": str(perturbation),
                "perturbation_type": perturbation_type,
                "genes": genes,
            }
        )
    return pd.DataFrame(rows)


def _split_class(
    genes: tuple[str, ...],
    perturbation_type: str,
    seen_genes: set[str],
) -> str:
    if perturbation_type == "control":
        return "control"
    if perturbation_type == "single":
        return "single_seen" if genes and genes[0] in seen_genes else "single_unseen"
    seen_count = sum(gene in seen_genes for gene in genes)
    if seen_count == 0:
        return "seen0"
    if seen_count == 1:
        return "seen1"
    return "seen2"


def _select_test_combos(
    perturbations: pd.DataFrame,
    *,
    rng: np.random.Generator,
    test_combo_fraction: float,
    min_test_combos_per_class: int,
) -> set[str]:
    combos = perturbations[perturbations["perturbation_type"] == "combo"]
    selected: set[str] = set()
    for split_class, group in combos.groupby("split_class", sort=True):
        del split_class
        n = max(min_test_combos_per_class, int(np.ceil(len(group) * test_combo_fraction)))
        n = min(n, len(group))
        chosen = rng.choice(group["perturbation"].to_numpy(dtype=object), size=n, replace=False)
        selected.update(map(str, chosen))
    return selected


def _perturbations_by_split(split_manifest: pd.DataFrame, split: str) -> list[str]:
    perturbations = split_manifest.loc[
        split_manifest["split"] == split,
        "perturbation",
    ].astype(str)
    return sorted(set(perturbations))


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
