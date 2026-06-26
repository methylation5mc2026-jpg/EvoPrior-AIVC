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


def test_prepare_gene_prior_hgnc_local_tsv_builds_real_metadata_features(tmp_path: Path):
    local = tmp_path / "hgnc.tsv"
    pd.DataFrame(
        {
            "hgnc_id": ["HGNC:1", "HGNC:2"],
            "symbol": ["A1BG", "IFIT1"],
            "name": ["alpha-1-B glycoprotein", "interferon induced protein"],
            "locus_group": ["protein-coding gene", "protein-coding gene"],
            "locus_type": ["gene with protein product", "gene with protein product"],
            "gene_group": ["", "Immunity|Interferon induced genes"],
        }
    ).to_csv(local, sep="\t", index=False)
    config = {
        "prior_id": "hgnc_prior",
        "output_root": str(tmp_path / "out"),
        "source": {
            "mode": "hgnc_local_tsv",
            "path": str(local),
            "source_version": "test-hgnc",
        },
    }

    result = prepare_gene_prior(config)
    frame = pd.read_csv(result.feature_table_path)

    assert result.source_is_real is True
    assert result.source_kind == "real_functional_gene_metadata"
    assert result.row_count == 2
    assert "gene_biotype" in result.feature_columns
    assert frame.loc[frame["gene_symbol"] == "IFIT1", "is_immune_related"].item() == 1
    assert frame.loc[frame["gene_symbol"] == "IFIT1", "hgnc_gene_group_count"].item() == 2


def test_prepare_gene_prior_goa_local_gaf_counts_aspects(tmp_path: Path):
    local = tmp_path / "mini.gaf"
    gaf_rows = [
        [
            "UniProtKB",
            "P1",
            "IFIT1",
            "",
            "GO:0006955",
            "PMID:1",
            "IDA",
            "",
            "P",
            "immune protein",
            "",
            "protein",
            "taxon:9606",
            "20260101",
            "GOA",
            "",
            "",
        ],
        [
            "UniProtKB",
            "P1",
            "IFIT1",
            "",
            "GO:0005515",
            "PMID:1",
            "IDA",
            "",
            "F",
            "immune protein",
            "",
            "protein",
            "taxon:9606",
            "20260101",
            "GOA",
            "",
            "",
        ],
        [
            "UniProtKB",
            "P2",
            "A1BG",
            "",
            "GO:0005576",
            "PMID:2",
            "IDA",
            "",
            "C",
            "alpha protein",
            "",
            "protein",
            "taxon:9606",
            "20260101",
            "GOA",
            "",
            "",
        ],
    ]
    local.write_text(
        "\n".join(
            ["!gaf-version: 2.2", *["\t".join(row) for row in gaf_rows]]
        ),
        encoding="utf-8",
    )
    config = {
        "prior_id": "goa_prior",
        "output_root": str(tmp_path / "out"),
        "source": {
            "mode": "goa_local_gaf",
            "path": str(local),
            "source_version": "test-goa",
        },
    }

    result = prepare_gene_prior(config)
    frame = pd.read_csv(result.feature_table_path).set_index("gene_symbol")

    assert result.source_is_real is True
    assert frame.loc["IFIT1", "go_annotation_count"] == 2
    assert frame.loc["IFIT1", "go_bp_count"] == 1
    assert frame.loc["IFIT1", "go_mf_count"] == 1
    assert frame.loc["A1BG", "go_cc_count"] == 1


def test_prepare_gene_prior_bundled_fixture_is_not_real(tmp_path: Path):
    config = {
        "prior_id": "fixture_prior",
        "output_root": str(tmp_path / "out"),
        "source": {"mode": "bundled_small_fixture"},
    }

    result = prepare_gene_prior(config)

    assert result.source_is_real is False
    assert result.source_kind == "test_fixture"
    assert result.feature_table_path.exists()


def test_prepare_gene_prior_download_mode_fails_gracefully(tmp_path: Path):
    config = {
        "prior_id": "download_prior",
        "output_root": str(tmp_path / "out"),
        "source": {
            "mode": "download_hgnc",
            "url": "https://example.invalid/hgnc.txt",
            "cache_dir": str(tmp_path / "cache"),
            "timeout_seconds": 1,
        },
    }

    with pytest.raises(RuntimeError, match="could not download"):
        prepare_gene_prior(config)


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
