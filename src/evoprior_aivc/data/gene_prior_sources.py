"""Prepare versioned gene-prior feature tables from safe sources."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from evoprior_aivc.data.download import md5sum
from evoprior_aivc.data.real_loader import load_real_dataset
from evoprior_aivc.priors.gene_prior_table import GenePriorTable


@dataclass(frozen=True)
class GenePriorPreparationResult:
    """Result of preparing or planning a gene-prior table."""

    prior_id: str
    source_mode: str
    output_dir: Path
    feature_table_path: Path
    manifest_path: Path
    status: str
    checksum: str | None
    message: str

    def to_dict(self) -> dict[str, str | None]:
        return {
            "prior_id": self.prior_id,
            "source_mode": self.source_mode,
            "output_dir": str(self.output_dir),
            "feature_table_path": str(self.feature_table_path),
            "manifest_path": str(self.manifest_path),
            "status": self.status,
            "checksum": self.checksum,
            "message": self.message,
        }


def prepare_gene_prior(
    config: dict[str, Any],
    *,
    dry_run: bool = False,
) -> GenePriorPreparationResult:
    """Prepare a gene-prior table according to a small source registry."""
    prior_id = config["prior_id"]
    source_mode = config["source"]["mode"]
    output_dir = Path(config["output_root"]) / prior_id
    feature_path = output_dir / "gene_prior_features.csv"
    manifest_path = output_dir / "manifest.json"

    if dry_run:
        return GenePriorPreparationResult(
            prior_id=prior_id,
            source_mode=source_mode,
            output_dir=output_dir,
            feature_table_path=feature_path,
            manifest_path=manifest_path,
            status="dry_run",
            checksum=None,
            message=_plan_message(config),
        )

    if source_mode == "synthetic_gene_prior":
        frame = _synthetic_gene_prior_frame(config)
    elif source_mode == "local_csv":
        frame = _local_csv_frame(config)
    elif source_mode in {
        "optional_ensembl_like_csv",
        "optional_orthodb_like_csv",
        "optional_go_like_csv",
    }:
        raise RuntimeError(
            f"{source_mode} is not implemented as an automatic downloader in v0.7; "
            "provide a local_csv with source/version/checksum instead."
        )
    else:
        raise ValueError(f"unsupported gene prior source mode: {source_mode}")

    table = GenePriorTable.from_dataframe(frame)
    output_dir.mkdir(parents=True, exist_ok=True)
    table.to_dataframe().to_csv(feature_path, index=False)
    checksum = md5sum(feature_path)
    manifest = {
        "prior_id": prior_id,
        "source_mode": source_mode,
        "feature_table_path": str(feature_path),
        "checksum_algorithm": "md5",
        "checksum": checksum,
        "n_genes": int(table.to_dataframe().shape[0]),
        "source": config["source"].get("source", source_mode),
        "source_version": config["source"].get("source_version", "unknown"),
        "claim_boundary": config.get("claim_boundary", ""),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return GenePriorPreparationResult(
        prior_id=prior_id,
        source_mode=source_mode,
        output_dir=output_dir,
        feature_table_path=feature_path,
        manifest_path=manifest_path,
        status="ready",
        checksum=checksum,
        message=f"prepared gene prior table at {feature_path}",
    )


def _synthetic_gene_prior_frame(config: dict[str, Any]) -> pd.DataFrame:
    source = config["source"]
    genes = _resolve_gene_list(config)
    missing_fraction = float(source.get("missing_fraction", 0.0))
    seed = int(source.get("seed", 0))
    rng = pd.Series(range(len(genes)), index=genes)
    missing_count = int(round(len(genes) * missing_fraction))
    missing_genes = set()
    if missing_count:
        sampled = rng.sample(n=missing_count, random_state=seed).index
        missing_genes = set(map(str, sampled))

    rows = []
    for idx, gene in enumerate(genes):
        if gene in missing_genes:
            conservation = None
            age = None
            orthologs = None
            expression_breadth = None
            housekeeping = None
            immune = None
            go = "unknown"
            pathway = "unknown"
        else:
            conservation = ((idx % 10) + 1) / 10.0
            age = float(idx % 6)
            orthologs = int(2 + (idx % 20))
            expression_breadth = ((idx * 3) % 10) / 10.0
            housekeeping = 1 if idx % 7 == 0 else 0
            immune = 1 if idx % 5 == 0 else 0
            go = ["core", "immune", "signaling", "metabolic"][idx % 4]
            pathway = ["housekeeping", "cytokine", "stress"][idx % 3]
        rows.append(
            {
                "gene_symbol": gene,
                "conservation_score": conservation,
                "gene_age_rank": age,
                "ortholog_count": orthologs,
                "paralog_count": int(idx % 4) if gene not in missing_genes else None,
                "expression_breadth": expression_breadth,
                "is_housekeeping": housekeeping,
                "is_immune_related": immune,
                "go_slim_category": go,
                "pathway_category": pathway,
                "source": source.get("source", "synthetic_gene_prior"),
                "source_version": source.get("source_version", "v0.7"),
            }
        )
    return pd.DataFrame(rows)


def _local_csv_frame(config: dict[str, Any]) -> pd.DataFrame:
    path = Path(config["source"]["path"])
    if not path.exists():
        raise FileNotFoundError(f"local gene prior CSV not found: {path}")
    frame = pd.read_csv(path)
    GenePriorTable.from_dataframe(frame)
    return frame


def _resolve_gene_list(config: dict[str, Any]) -> list[str]:
    source = config["source"]
    if "genes" in source:
        return [str(gene) for gene in source["genes"]]
    if source.get("data_config"):
        data_config = yaml.safe_load(Path(source["data_config"]).read_text(encoding="utf-8"))
        adata, _ = load_real_dataset(data_config)
        if "gene_symbol" in adata.var.columns:
            genes = list(map(str, adata.var["gene_symbol"]))
        else:
            genes = list(map(str, adata.var_names))
        max_genes = source.get("max_genes")
        if max_genes is not None:
            genes = genes[: int(max_genes)]
        return genes
    n_genes = int(source.get("n_genes", 20))
    prefix = source.get("gene_prefix", "GPRIOR")
    return [f"{prefix}{idx:04d}" for idx in range(n_genes)]


def _plan_message(config: dict[str, Any]) -> str:
    source_mode = config["source"]["mode"]
    if source_mode == "local_csv":
        source = config["source"].get("path", "missing path")
    elif source_mode == "synthetic_gene_prior":
        source = config["source"].get("data_config", "synthetic gene list")
    else:
        source = config["source"].get("url", "external source not configured")
    return (
        f"prior_id={config['prior_id']}; mode={source_mode}; source={source}; "
        f"output_root={config['output_root']}"
    )


def copy_prepared_gene_prior(src: Path, dst: Path) -> None:
    """Copy a prepared small prior table when a caller needs a local fixture."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
