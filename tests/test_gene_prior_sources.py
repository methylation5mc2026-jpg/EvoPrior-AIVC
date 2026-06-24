from pathlib import Path

import pandas as pd
import pytest

from evoprior_aivc.data.gene_prior_sources import prepare_gene_prior


def test_prepare_gene_prior_synthetic_writes_table_and_manifest(tmp_path: Path):
    config = _synthetic_config(tmp_path)

    dry = prepare_gene_prior(config, dry_run=True)
    result = prepare_gene_prior(config)

    assert dry.status == "dry_run"
    assert result.status == "ready"
    assert result.checksum is not None
    assert result.feature_table_path.exists()
    assert result.manifest_path.exists()
    frame = pd.read_csv(result.feature_table_path)
    assert frame.shape[0] == 5


def test_prepare_gene_prior_local_csv_validates_and_copies(tmp_path: Path):
    local = tmp_path / "manual.csv"
    pd.DataFrame(
        {
            "gene_symbol": ["A", "B"],
            "conservation_score": [0.1, 0.9],
            "source": ["manual", "manual"],
            "source_version": ["v1", "v1"],
        }
    ).to_csv(local, index=False)
    config = {
        "prior_id": "manual_prior",
        "output_root": str(tmp_path / "out"),
        "source": {"mode": "local_csv", "path": str(local)},
    }

    result = prepare_gene_prior(config)

    assert result.feature_table_path.exists()
    assert pd.read_csv(result.feature_table_path)["gene_symbol"].tolist() == ["A", "B"]


def test_prepare_gene_prior_external_mode_fails_gracefully(tmp_path: Path):
    config = {
        "prior_id": "external_prior",
        "output_root": str(tmp_path / "out"),
        "source": {"mode": "optional_ensembl_like_csv", "url": "https://example.invalid"},
    }

    with pytest.raises(RuntimeError, match="not implemented"):
        prepare_gene_prior(config)


def _synthetic_config(tmp_path: Path):
    return {
        "prior_id": "toy_prior",
        "output_root": str(tmp_path),
        "source": {
            "mode": "synthetic_gene_prior",
            "source": "synthetic_gene_prior",
            "source_version": "test",
            "genes": ["A", "B", "C", "D", "E"],
            "missing_fraction": 0.2,
            "seed": 1,
        },
    }
