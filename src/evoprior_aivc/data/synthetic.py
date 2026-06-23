"""Deterministic synthetic perturbation data for engineering tests."""

from __future__ import annotations

import numpy as np
import pandas as pd
from anndata import AnnData
from scipy import sparse

from evoprior_aivc.data.validate import normalize_metadata_labels


def make_synthetic_perturbation_adata(
    *,
    n_genes: int = 20,
    cells_per_group: int = 6,
    seed: int = 0,
    sparse_x: bool = False,
) -> AnnData:
    """Create a small AnnData object with known perturbation and cell effects."""
    if n_genes < 20:
        raise ValueError("n_genes must be at least 20")
    if cells_per_group < 2:
        raise ValueError("cells_per_group must be at least 2")

    rng = np.random.default_rng(seed)
    cell_types = ("t_cell", "b_cell", "monocyte")
    perturbations = ("control", "pert_a", "pert_b", "pert_c")
    donors = ("donor_1", "donor_2")
    gene_ids = np.array([f"ENSG_SYN_{idx:05d}" for idx in range(n_genes)])
    gene_symbols = np.array([f"GENE{idx:02d}" for idx in range(n_genes)])

    rows: list[np.ndarray] = []
    obs_records: list[dict[str, object]] = []
    base = 8.0 + np.linspace(0.0, 2.0, n_genes)
    perturbation_delta = _perturbation_delta_matrix(n_genes)
    cell_type_effects = {
        "t_cell": np.zeros(n_genes),
        "b_cell": _single_gene_effect(n_genes, 1, 0.7),
        "monocyte": _single_gene_effect(n_genes, 2, -0.6),
    }
    donor_effects = {
        "donor_1": np.zeros(n_genes),
        "donor_2": np.full(n_genes, 0.15),
    }

    for cell_type in cell_types:
        for perturbation in perturbations:
            for donor in donors:
                deterministic_mean = (
                    base
                    + cell_type_effects[cell_type]
                    + donor_effects[donor]
                    + perturbation_delta[perturbation]
                    + _cell_specific_delta(n_genes, cell_type, perturbation)
                )
                for replicate in range(cells_per_group):
                    noise = rng.normal(loc=0.0, scale=0.02, size=n_genes)
                    rows.append(np.clip(deterministic_mean + noise, a_min=0.0, a_max=None))
                    obs_records.append(
                        {
                            "cell_type": cell_type,
                            "perturbation": perturbation,
                            "is_control": perturbation == "control",
                            "donor": donor,
                            "batch": f"batch_{1 + (replicate % 2)}",
                            "tissue": "blood",
                            "dose": "synthetic",
                            "time": "24h",
                        }
                    )

    x = np.vstack(rows)
    if sparse_x:
        x = sparse.csr_matrix(x)

    obs = pd.DataFrame(obs_records)
    obs.index = [f"cell_{idx:04d}" for idx in range(obs.shape[0])]
    var = pd.DataFrame(
        {
            "gene_id": gene_ids,
            "gene_symbol": gene_symbols,
            "highly_variable": [idx < min(10, n_genes) for idx in range(n_genes)],
            "gene_biotype": ["protein_coding"] * n_genes,
        },
        index=gene_symbols,
    )
    adata = AnnData(X=x, obs=obs, var=var)
    adata.uns["synthetic_design"] = {
        "cell_types": list(cell_types),
        "perturbations": list(perturbations),
        "donors": list(donors),
        "cells_per_group": cells_per_group,
        "known_delta_genes": {
            "pert_a": ["GENE00", "GENE01", "GENE02", "GENE03", "GENE04"],
            "pert_b": ["GENE05", "GENE06", "GENE07", "GENE08", "GENE09"],
            "pert_c": ["GENE10", "GENE11", "GENE12", "GENE13", "GENE14"],
        },
    }
    return normalize_metadata_labels(adata)


def _perturbation_delta_matrix(n_genes: int) -> dict[str, np.ndarray]:
    deltas = {
        "control": np.zeros(n_genes),
        "pert_a": np.zeros(n_genes),
        "pert_b": np.zeros(n_genes),
        "pert_c": np.zeros(n_genes),
    }
    deltas["pert_a"][:5] = 2.0
    deltas["pert_b"][5:10] = -1.5
    deltas["pert_c"][10:15] = 1.2
    deltas["pert_c"][15:20] = -0.7
    return deltas


def _cell_specific_delta(n_genes: int, cell_type: str, perturbation: str) -> np.ndarray:
    delta = np.zeros(n_genes)
    if cell_type == "b_cell" and perturbation == "pert_a":
        delta[0] = 0.8
    if cell_type == "monocyte" and perturbation == "pert_b":
        delta[5] = -0.9
    return delta


def _single_gene_effect(n_genes: int, gene_idx: int, value: float) -> np.ndarray:
    effect = np.zeros(n_genes)
    effect[gene_idx] = value
    return effect

