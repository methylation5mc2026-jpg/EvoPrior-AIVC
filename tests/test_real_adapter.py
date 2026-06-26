from pathlib import Path

import anndata as ad
import numpy as np
import pandas as pd

from evoprior_aivc.data.real_loader import load_real_dataset
from evoprior_aivc.data.validate import validate_adata_schema


def test_generic_h5ad_adapter_maps_messy_metadata(tmp_path):
    path = _write_tiny_h5ad(tmp_path)
    config = _config(path)

    adata, report = load_real_dataset(config, schema_report_dir=tmp_path / "report")

    validate_adata_schema(adata)
    assert "cell_type" in adata.obs.columns
    assert "perturbation" in adata.obs.columns
    assert "is_control" in adata.obs.columns
    assert "gene_symbol" in adata.var.columns
    assert "gene_id" in adata.var.columns
    assert int(adata.obs["is_control"].sum()) == 2
    assert report.final_decision == "usable with limitations"
    assert (tmp_path / "report" / "schema_report.md").exists()


def _write_tiny_h5ad(tmp_path: Path) -> Path:
    obs = pd.DataFrame(
        {
            "Perturbation Label": [" Control ", "CTRL", "GeneA", "GeneB"],
            "Cell Kind": ["T Cell", "T Cell", "B Cell", "B Cell"],
            "guide_id": ["nt1", "nt2", "g1", "g2"],
        },
        index=[f"cell{i}" for i in range(4)],
    )
    var = pd.DataFrame(
        {"ensembl": ["ENSG1", "ENSG2", "ENSG3"]},
        index=["Gene 1", "Gene 2", "Gene 3"],
    )
    adata = ad.AnnData(X=np.ones((4, 3)), obs=obs, var=var)
    path = tmp_path / "toy_real.h5ad"
    adata.write_h5ad(path)
    return path


def _config(path: Path):
    return {
        "dataset": {
            "dataset_id": "toy_real",
            "display_name": "Toy real",
            "source_url": None,
            "expected_raw_path": str(path),
            "expected_format": "h5ad",
            "checksum": "checksum unavailable",
            "checksum_algorithm": None,
            "license": "test",
            "access_notes": "test only",
            "adapter": "generic_h5ad",
        },
        "prepare": {"mode": "local_or_download", "local_path": None},
        "adapter": {
            "obs_mapping": {
                "perturbation": "Perturbation Label",
                "cell_type": "Cell Kind",
                "donor": None,
                "batch": None,
                "tissue": None,
                "dose": None,
                "time": None,
            },
            "var_mapping": {"gene_symbol": None, "gene_id": "ensembl"},
            "control_labels": ["control", "ctrl"],
            "fallback_cell_type": "unknown_cell_type",
            "preserve_obs_fields": ["guide_id"],
        },
    }

