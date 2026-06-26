"""Synthetic multi-cell-type perturbation data with known lineage effects."""

from __future__ import annotations

import numpy as np
import pandas as pd
from anndata import AnnData

from evoprior_aivc.data.validate import normalize_metadata_labels
from evoprior_aivc.priors.cell_lineage import LineageTree

LINEAGE_EDGES: tuple[tuple[str | None, str], ...] = (
    (None, "root"),
    ("root", "immune"),
    ("immune", "myeloid"),
    ("immune", "lymphoid"),
    ("myeloid", "myeloid_a"),
    ("myeloid", "myeloid_b"),
    ("lymphoid", "lymphoid_a"),
    ("lymphoid", "lymphoid_b"),
    ("root", "epithelial"),
    ("epithelial", "epithelial_a"),
    ("epithelial", "epithelial_b"),
    ("root", "stromal"),
    ("stromal", "stromal_a"),
    ("stromal", "stromal_b"),
)

CELL_TYPES: tuple[str, ...] = (
    "myeloid_a",
    "myeloid_b",
    "lymphoid_a",
    "lymphoid_b",
    "epithelial_a",
    "epithelial_b",
    "stromal_a",
    "stromal_b",
)

PERTURBATIONS: tuple[str, ...] = ("control", "stim_a", "stim_b", "stim_c", "stim_d", "stim_e")


def make_synthetic_lineage_tree() -> LineageTree:
    """Return the default synthetic lineage tree."""
    return LineageTree.from_edges(LINEAGE_EDGES)


def make_synthetic_lineage_adata(
    *,
    n_genes: int = 40,
    cells_per_group: int = 5,
    seed: int = 0,
) -> AnnData:
    """Create synthetic lineage-structured perturbation AnnData."""
    if n_genes < 30:
        raise ValueError("n_genes must be at least 30")
    if cells_per_group < 2:
        raise ValueError("cells_per_group must be at least 2")

    rng = np.random.default_rng(seed)
    base = 5.0 + np.linspace(0.0, 1.0, n_genes)
    perturbation_effects = _perturbation_effects(n_genes)
    clade_effects = _clade_effects(n_genes)
    cell_effects = _cell_type_effects(n_genes)
    donors = ("donor_1", "donor_2")
    batches = ("batch_1", "batch_2")

    rows: list[np.ndarray] = []
    obs_records: list[dict[str, object]] = []
    for cell_type in CELL_TYPES:
        clade = _major_clade(cell_type)
        for perturbation in PERTURBATIONS:
            for donor_idx, donor in enumerate(donors):
                mean = (
                    base
                    + _donor_effect(n_genes, donor_idx)
                    + cell_effects[cell_type]
                    + perturbation_effects[perturbation]
                    + clade_effects[clade][perturbation]
                )
                for replicate in range(cells_per_group):
                    noise = rng.normal(0.0, 0.015, size=n_genes)
                    rows.append(np.clip(mean + noise, a_min=0.0, a_max=None))
                    obs_records.append(
                        {
                            "cell_type": cell_type,
                            "perturbation": perturbation,
                            "is_control": perturbation == "control",
                            "donor": donor,
                            "batch": batches[(replicate + donor_idx) % len(batches)],
                            "tissue": "synthetic_lineage",
                        }
                    )

    obs = pd.DataFrame(obs_records)
    obs.index = [f"lineage_cell_{idx:05d}" for idx in range(obs.shape[0])]
    var = pd.DataFrame(
        {
            "gene_id": [f"ENSG_LINEAGE_{idx:05d}" for idx in range(n_genes)],
            "gene_symbol": [f"LGENE{idx:02d}" for idx in range(n_genes)],
            "gene_biotype": ["protein_coding"] * n_genes,
            "highly_variable": [idx < min(20, n_genes) for idx in range(n_genes)],
        },
        index=[f"LGENE{idx:02d}" for idx in range(n_genes)],
    )
    adata = AnnData(X=np.vstack(rows), obs=obs, var=var)
    adata.uns["synthetic_lineage_design"] = {
        "lineage_edges": list(LINEAGE_EDGES),
        "cell_types": list(CELL_TYPES),
        "perturbations": list(PERTURBATIONS),
        "response_structure": "global perturbation + clade effect + cell-type effect + noise",
    }
    return normalize_metadata_labels(adata)


def heldout_cell_type_split(metadata: pd.DataFrame, *, heldout_cell_type: str) -> pd.Series:
    """Assign train/test labels for a held-out cell type at pseudobulk group level."""
    if "cell_type" not in metadata.columns:
        raise KeyError("metadata must include cell_type")
    split = pd.Series("train", index=metadata.index, dtype="object")
    split.loc[metadata["cell_type"] == heldout_cell_type] = "test"
    if not (split == "test").any():
        raise ValueError(f"heldout cell type has no groups: {heldout_cell_type}")
    if not (split == "train").any():
        raise ValueError("heldout split leaves no training groups")
    return split.astype("category")


def _perturbation_effects(n_genes: int) -> dict[str, np.ndarray]:
    effects = {perturbation: np.zeros(n_genes) for perturbation in PERTURBATIONS}
    for idx, perturbation in enumerate(PERTURBATIONS[1:]):
        start = (idx * 5) % n_genes
        end = min(start + 5, n_genes)
        effects[perturbation][start:end] = 0.8 + idx * 0.15
    return effects


def _clade_effects(n_genes: int) -> dict[str, dict[str, np.ndarray]]:
    effects: dict[str, dict[str, np.ndarray]] = {}
    for clade_idx, clade in enumerate(("myeloid", "lymphoid", "epithelial", "stromal")):
        effects[clade] = {}
        for perturb_idx, perturbation in enumerate(PERTURBATIONS):
            values = np.zeros(n_genes)
            if perturbation != "control":
                start = (20 + clade_idx * 3 + perturb_idx) % n_genes
                values[start : min(start + 3, n_genes)] = 1.0 + 0.2 * clade_idx
                if clade == "myeloid" and perturbation == "stim_a":
                    values[:6] += 1.4
                if clade == "lymphoid" and perturbation == "stim_b":
                    values[6:12] += 1.1
            effects[clade][perturbation] = values
    return effects


def _cell_type_effects(n_genes: int) -> dict[str, np.ndarray]:
    effects = {}
    for idx, cell_type in enumerate(CELL_TYPES):
        values = np.zeros(n_genes)
        values[(idx + 2) % n_genes] = 0.15
        effects[cell_type] = values
    return effects


def _donor_effect(n_genes: int, donor_idx: int) -> np.ndarray:
    return np.full(n_genes, donor_idx * 0.05)


def _major_clade(cell_type: str) -> str:
    if cell_type.startswith("myeloid"):
        return "myeloid"
    if cell_type.startswith("lymphoid"):
        return "lymphoid"
    if cell_type.startswith("epithelial"):
        return "epithelial"
    if cell_type.startswith("stromal"):
        return "stromal"
    raise ValueError(f"unknown synthetic cell type: {cell_type}")
