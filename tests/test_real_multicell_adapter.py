from pathlib import Path

import numpy as np
import pandas as pd
from anndata import AnnData

from evoprior_aivc.data.real_loader import load_real_dataset


def test_generic_h5ad_adapter_reports_multicell_coverage(tmp_path: Path):
    path = tmp_path / "toy_multicell.h5ad"
    adata = AnnData(
        X=np.ones((6, 3), dtype=float),
        obs=pd.DataFrame(
            {
                "label": ["ctrl", "stim", "ctrl", "stim", "ctrl", "stim"],
                "cell_type": ["T", "T", "B", "B", "Mono", "Mono"],
                "replicate": ["p1", "p1", "p1", "p1", "p2", "p2"],
            },
            index=[f"cell_{idx}" for idx in range(6)],
        ),
        var=pd.DataFrame(
            {"name": ["G1", "G2", "G3"]},
            index=["g1", "g2", "g3"],
        ),
    )
    adata.write_h5ad(path)

    config = _config(path)
    mapped, report = load_real_dataset(config, schema_report_dir=tmp_path / "schema")

    assert mapped.obs["is_control"].tolist() == [True, False, True, False, True, False]
    assert report.n_cell_types == 3
    assert report.n_perturbations == 2
    assert report.coverage_summary["observed_cell_type_perturbation_pairs"] == 6
    schema_text = (tmp_path / "schema" / "schema_report.md").read_text(encoding="utf-8")
    assert "Cell Type x Perturbation Coverage" in schema_text


def _config(path: Path):
    return {
        "dataset": {
            "dataset_id": "toy_multicell",
            "display_name": "Toy multicell",
            "source_url": None,
            "expected_raw_path": str(path),
            "expected_format": "h5ad",
            "checksum": "checksum unavailable",
            "checksum_algorithm": None,
            "license": "test",
            "access_notes": "test only",
            "adapter": "generic_h5ad",
            "allow_auto_download": False,
        },
        "prepare": {"mode": "manual", "local_path": None},
        "adapter": {
            "obs_mapping": {
                "perturbation": "label",
                "cell_type": "cell_type",
                "donor": "replicate",
                "batch": None,
                "tissue": None,
                "dose": None,
                "time": None,
            },
            "var_mapping": {"gene_symbol": "name", "gene_id": None},
            "control_labels": ["ctrl"],
        },
    }
