"""Synthetic perturbation data with known gene-prior modulation."""

from __future__ import annotations

import numpy as np
import pandas as pd
from anndata import AnnData

from evoprior_aivc.data.validate import normalize_metadata_labels
from evoprior_aivc.priors.cell_lineage import LineageTree
from evoprior_aivc.priors.gene_prior_table import GenePriorTable

GENE_PRIOR_CELL_TYPES: tuple[str, ...] = (
    "cd4_like",
    "cd8_like",
    "b_like",
    "nk_like",
    "mono_like",
    "dc_like",
)
GENE_PRIOR_PERTURBATIONS: tuple[str, ...] = (
    "control",
    "stim_a",
    "stim_b",
    "stim_c",
    "stim_d",
    "stim_e",
)
GENE_PRIOR_LINEAGE_EDGES: tuple[tuple[str | None, str], ...] = (
    (None, "root"),
    ("root", "immune"),
    ("immune", "lymphoid"),
    ("lymphoid", "t_like"),
    ("t_like", "cd4_like"),
    ("t_like", "cd8_like"),
    ("lymphoid", "b_like"),
    ("lymphoid", "nk_like"),
    ("immune", "myeloid"),
    ("myeloid", "mono_like"),
    ("myeloid", "dc_like"),
)


def make_synthetic_gene_prior_tree() -> LineageTree:
    """Return the default synthetic gene-prior lineage tree."""
    return LineageTree.from_edges(GENE_PRIOR_LINEAGE_EDGES)


def make_synthetic_gene_prior_table(n_genes: int = 120) -> GenePriorTable:
    """Create a toy gene-prior table with known feature blocks."""
    if n_genes < 100:
        raise ValueError("n_genes must be at least 100")
    rows = []
    for idx in range(n_genes):
        gene = f"SGENE{idx:03d}"
        missing = idx >= n_genes - 15
        conserved = idx < 30
        immune = 30 <= idx < 60
        young = 60 <= idx < 90
        gene_age_rank = 0.0 if conserved else 4.0 if young else 2.0
        go_slim_category = "core" if conserved else "immune" if immune else "other"
        pathway_category = "housekeeping" if conserved else "cytokine" if immune else "stress"
        rows.append(
            {
                "gene_symbol": gene,
                "conservation_score": None if missing else (0.9 if conserved else 0.35),
                "gene_age_rank": None if missing else gene_age_rank,
                "ortholog_count": None if missing else (30 if conserved else (6 if young else 14)),
                "paralog_count": None if missing else idx % 4,
                "expression_breadth": None if missing else (0.85 if conserved else 0.45),
                "is_housekeeping": None if missing else int(conserved),
                "is_immune_related": None if missing else int(immune),
                "go_slim_category": "unknown" if missing else go_slim_category,
                "pathway_category": "unknown" if missing else pathway_category,
                "source": "synthetic_gene_prior",
                "source_version": "v0.7-synthetic",
            }
        )
    return GenePriorTable.from_dataframe(pd.DataFrame(rows))


def make_synthetic_gene_prior_adata(
    *,
    n_genes: int = 120,
    cells_per_group: int = 5,
    seed: int = 0,
) -> tuple[AnnData, GenePriorTable]:
    """Create synthetic AnnData where response deltas depend on gene-prior features."""
    if cells_per_group < 2:
        raise ValueError("cells_per_group must be at least 2")
    prior = make_synthetic_gene_prior_table(n_genes)
    rng = np.random.default_rng(seed)
    base = 4.0 + np.linspace(0.0, 0.8, n_genes)
    donors = ("donor_1", "donor_2")
    rows: list[np.ndarray] = []
    obs_records: list[dict[str, object]] = []
    for cell_type in GENE_PRIOR_CELL_TYPES:
        lineage = _major_lineage(cell_type)
        for perturbation in GENE_PRIOR_PERTURBATIONS:
            for donor_idx, donor in enumerate(donors):
                mean = (
                    base
                    + _cell_type_effect(cell_type, n_genes)
                    + donor_idx * 0.03
                    + _perturbation_effect(perturbation, n_genes)
                    + _lineage_effect(lineage, perturbation, n_genes)
                    + _gene_prior_modulation(perturbation, n_genes)
                )
                for replicate in range(cells_per_group):
                    noise = rng.normal(0.0, 0.02, size=n_genes)
                    rows.append(np.clip(mean + noise, a_min=0.0, a_max=None))
                    obs_records.append(
                        {
                            "cell_type": cell_type,
                            "perturbation": perturbation,
                            "is_control": perturbation == "control",
                            "donor": donor,
                            "batch": f"batch_{1 + ((replicate + donor_idx) % 2)}",
                            "tissue": "synthetic_gene_prior",
                        }
                    )
    obs = pd.DataFrame(obs_records)
    obs.index = [f"gene_prior_cell_{idx:05d}" for idx in range(obs.shape[0])]
    var = pd.DataFrame(
        {
            "gene_id": [f"ENSG_SYN_GP_{idx:05d}" for idx in range(n_genes)],
            "gene_symbol": [f"SGENE{idx:03d}" for idx in range(n_genes)],
            "gene_biotype": ["protein_coding"] * n_genes,
            "highly_variable": [idx < min(50, n_genes) for idx in range(n_genes)],
        },
        index=[f"SGENE{idx:03d}" for idx in range(n_genes)],
    )
    adata = AnnData(X=np.vstack(rows), obs=obs, var=var)
    adata.uns["synthetic_gene_prior_design"] = {
        "response_structure": "lineage + perturbation + gene-prior modulation + noise",
        "prior_modulated_gene_blocks": {
            "conserved_core": "SGENE000-SGENE029",
            "immune_related": "SGENE030-SGENE059",
            "young_context": "SGENE060-SGENE089",
            "missing_prior": f"last 15 genes through SGENE{n_genes - 1:03d}",
        },
    }
    return normalize_metadata_labels(adata), prior


def _perturbation_effect(perturbation: str, n_genes: int) -> np.ndarray:
    effect = np.zeros(n_genes)
    if perturbation == "control":
        return effect
    idx = GENE_PRIOR_PERTURBATIONS.index(perturbation) - 1
    start = 10 + idx * 4
    effect[start : start + 6] = 0.4 + idx * 0.05
    return effect


def _gene_prior_modulation(perturbation: str, n_genes: int) -> np.ndarray:
    effect = np.zeros(n_genes)
    if perturbation == "control":
        return effect
    effect[:30] += 0.25
    if perturbation in {"stim_a", "stim_b", "stim_c"}:
        effect[30:60] += 0.9
    if perturbation in {"stim_d", "stim_e"}:
        effect[60:90] += 0.45
    return effect


def _lineage_effect(lineage: str, perturbation: str, n_genes: int) -> np.ndarray:
    effect = np.zeros(n_genes)
    if perturbation == "control":
        return effect
    if lineage == "lymphoid":
        effect[35:45] += 0.25
    if lineage == "myeloid":
        effect[45:55] += 0.35
    return effect


def _cell_type_effect(cell_type: str, n_genes: int) -> np.ndarray:
    idx = GENE_PRIOR_CELL_TYPES.index(cell_type)
    effect = np.zeros(n_genes)
    effect[(idx * 3) % n_genes] = 0.1
    return effect


def _major_lineage(cell_type: str) -> str:
    return "myeloid" if cell_type in {"mono_like", "dc_like"} else "lymphoid"
