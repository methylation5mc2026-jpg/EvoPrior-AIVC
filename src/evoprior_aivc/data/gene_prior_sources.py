"""Prepare versioned gene-prior feature tables from safe sources."""

from __future__ import annotations

import gzip
import hashlib
import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen

import pandas as pd
import yaml

from evoprior_aivc.data.download import md5sum
from evoprior_aivc.data.real_loader import load_real_dataset
from evoprior_aivc.priors.gene_prior_table import GenePriorTable

DEFAULT_HGNC_URL = (
    "https://storage.googleapis.com/public-download-files/hgnc/tsv/tsv/hgnc_complete_set.txt"
)
DEFAULT_GOA_HUMAN_URL = "https://current.geneontology.org/annotations/goa_human.gaf.gz"
IMMUNE_KEYWORDS = (
    "immune",
    "immunoglobulin",
    "interferon",
    "interleukin",
    "cytokine",
    "chemokine",
    "hla",
    "antigen",
    "t cell",
    "b cell",
    "leukocyte",
)


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
    source_is_real: bool = False
    source_kind: str = "unknown"
    row_count: int | None = None
    feature_columns: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "prior_id": self.prior_id,
            "source_mode": self.source_mode,
            "output_dir": str(self.output_dir),
            "feature_table_path": str(self.feature_table_path),
            "manifest_path": str(self.manifest_path),
            "status": self.status,
            "checksum": self.checksum,
            "message": self.message,
            "source_is_real": self.source_is_real,
            "source_kind": self.source_kind,
            "row_count": self.row_count,
            "feature_columns": list(self.feature_columns),
        }


@dataclass(frozen=True)
class _SourceBuild:
    frame: pd.DataFrame
    source_files: tuple[dict[str, str | None], ...]
    source_is_real: bool
    source_kind: str


def prepare_gene_prior(
    config: dict[str, Any],
    *,
    dry_run: bool = False,
) -> GenePriorPreparationResult:
    """Prepare a gene-prior table according to a small source registry."""
    prior_id = config["prior_id"]
    source_mode = config["source"]["mode"]
    output_dir = _resolve_output_dir(config)
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
            source_is_real=_source_is_real_for_config(config),
            source_kind=_source_kind_for_config(config),
        )

    build = _build_source(config)
    table = GenePriorTable.from_dataframe(build.frame)
    output_dir.mkdir(parents=True, exist_ok=True)
    table.to_dataframe().to_csv(feature_path, index=False)
    checksum = md5sum(feature_path)
    sha256 = _sha256sum(feature_path)
    feature_columns = tuple(table.feature_columns)
    manifest = {
        "prior_id": prior_id,
        "source_mode": source_mode,
        "source_kind": build.source_kind,
        "source_is_real": build.source_is_real,
        "feature_table_path": str(feature_path),
        "feature_table_checksums": {"md5": checksum, "sha256": sha256},
        "n_genes": int(table.to_dataframe().shape[0]),
        "feature_columns": list(feature_columns),
        "prepared_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git_commit": _git_commit(),
        "source_files": list(build.source_files),
        "source": config["source"].get("source", source_mode),
        "source_version": config["source"].get("source_version", "unknown"),
        "source_url": config["source"].get("url"),
        "manual_note": config["source"].get("manual_note"),
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
        source_is_real=build.source_is_real,
        source_kind=build.source_kind,
        row_count=int(table.to_dataframe().shape[0]),
        feature_columns=feature_columns,
    )


def _build_source(config: dict[str, Any]) -> _SourceBuild:
    source_mode = config["source"]["mode"]
    if source_mode == "synthetic_gene_prior":
        return _SourceBuild(
            frame=_synthetic_gene_prior_frame(config),
            source_files=(),
            source_is_real=False,
            source_kind="synthetic_placeholder",
        )
    if source_mode in {"local_csv", "local_curated_gene_prior_csv"}:
        path = Path(config["source"]["path"])
        return _SourceBuild(
            frame=_local_csv_frame(config),
            source_files=(_source_file_record(path, role="local_curated_gene_prior_csv"),),
            source_is_real=bool(config["source"].get("source_is_real", True)),
            source_kind=config["source"].get("source_kind", "local_curated_gene_prior"),
        )
    if source_mode == "hgnc_local_tsv":
        path = Path(config["source"]["path"])
        return _SourceBuild(
            frame=_hgnc_frame(path, config),
            source_files=(_source_file_record(path, role="hgnc_complete_set"),),
            source_is_real=True,
            source_kind="real_functional_gene_metadata",
        )
    if source_mode == "goa_local_gaf":
        path = Path(config["source"]["path"])
        return _SourceBuild(
            frame=_goa_gaf_frame(path, config),
            source_files=(_source_file_record(path, role="goa_gaf"),),
            source_is_real=True,
            source_kind="real_functional_go_annotation",
        )
    if source_mode == "bundled_small_fixture":
        return _SourceBuild(
            frame=_bundled_small_fixture_frame(config),
            source_files=(),
            source_is_real=False,
            source_kind="test_fixture",
        )
    if source_mode == "download_hgnc":
        url = config["source"].get("url", DEFAULT_HGNC_URL)
        path = _download_source_file(config, url=url, filename="hgnc_complete_set.txt")
        return _SourceBuild(
            frame=_hgnc_frame(path, config),
            source_files=(_source_file_record(path, role="hgnc_complete_set", url=url),),
            source_is_real=True,
            source_kind="real_functional_gene_metadata",
        )
    if source_mode == "download_goa":
        url = config["source"].get("url", DEFAULT_GOA_HUMAN_URL)
        path = _download_source_file(config, url=url, filename="goa_human.gaf.gz")
        return _SourceBuild(
            frame=_goa_gaf_frame(path, config),
            source_files=(_source_file_record(path, role="goa_gaf", url=url),),
            source_is_real=True,
            source_kind="real_functional_go_annotation",
        )
    if source_mode in {
        "optional_ensembl_like_csv",
        "optional_orthodb_like_csv",
        "optional_go_like_csv",
    }:
        raise RuntimeError(
            f"{source_mode} is not implemented as an automatic downloader in v0.8; "
            "provide a local_curated_gene_prior_csv with source/version/checksum instead."
        )
    raise ValueError(f"unsupported gene prior source mode: {source_mode}")


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
    if "source" not in frame.columns:
        frame["source"] = config["source"].get("source", "local_curated_gene_prior_csv")
    if "source_version" not in frame.columns:
        frame["source_version"] = config["source"].get("source_version", "unknown")
    GenePriorTable.from_dataframe(frame)
    return frame


def _hgnc_frame(path: Path, config: dict[str, Any]) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"HGNC TSV not found: {path}")
    raw = pd.read_csv(path, sep="\t", dtype=str)
    symbol_column = _first_existing(raw, ("symbol", "approved_symbol"))
    hgnc_id_column = _first_existing(raw, ("hgnc_id", "HGNC ID"))
    locus_group_column = _first_existing(raw, ("locus_group",))
    locus_type_column = _first_existing(raw, ("locus_type",))
    gene_group_column = _first_existing(raw, ("gene_group", "gene_group_id"))
    name_column = _first_existing(raw, ("name",))
    source = config["source"]
    rows = []
    for _, row in raw.iterrows():
        symbol = _clean_scalar(row.get(symbol_column))
        if not symbol:
            continue
        gene_group = _clean_scalar(row.get(gene_group_column)) if gene_group_column else ""
        name = _clean_scalar(row.get(name_column)) if name_column else ""
        locus_group = (
            _clean_scalar(row.get(locus_group_column)) if locus_group_column else "unknown"
        )
        locus_type = _clean_scalar(row.get(locus_type_column)) if locus_type_column else "unknown"
        searchable = " ".join([symbol, gene_group, name, locus_group, locus_type]).lower()
        rows.append(
            {
                "gene_symbol": symbol,
                "gene_id": _clean_scalar(row.get(hgnc_id_column)) if hgnc_id_column else symbol,
                "approved_symbol_present": 1,
                "gene_biotype": locus_type or "unknown",
                "locus_group": locus_group or "unknown",
                "hgnc_gene_group_count": _pipe_count(gene_group),
                "is_immune_related": int(any(keyword in searchable for keyword in IMMUNE_KEYWORDS)),
                "source": source.get("source", "HGNC complete set"),
                "source_version": source.get("source_version", "unknown"),
            }
        )
    return pd.DataFrame(rows)


def _goa_gaf_frame(path: Path, config: dict[str, Any]) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"GOA GAF not found: {path}")
    columns = [
        "db",
        "db_object_id",
        "gene_symbol",
        "qualifier",
        "go_id",
        "db_reference",
        "evidence_code",
        "with_or_from",
        "aspect",
        "db_object_name",
        "synonym",
        "object_type",
        "taxon",
        "date",
        "assigned_by",
        "annotation_extension",
        "gene_product_form_id",
    ]
    opener = gzip.open if path.suffix == ".gz" else open
    records = []
    with opener(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip() or line.startswith("!"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 17:
                continue
            records.append(parts[:17])
    if not records:
        raise ValueError(f"GOA GAF did not contain annotation records: {path}")
    raw = pd.DataFrame(records, columns=columns)
    raw["aspect"] = raw["aspect"].astype(str).str.upper()
    grouped = raw.groupby("gene_symbol", dropna=False)
    source = config["source"]
    rows = []
    for symbol, frame in grouped:
        searchable = " ".join(frame["db_object_name"].dropna().astype(str).head(20)).lower()
        rows.append(
            {
                "gene_symbol": str(symbol),
                "go_annotation_count": int(frame.shape[0]),
                "go_bp_count": int((frame["aspect"] == "P").sum()),
                "go_mf_count": int((frame["aspect"] == "F").sum()),
                "go_cc_count": int((frame["aspect"] == "C").sum()),
                "is_immune_related": int(any(keyword in searchable for keyword in IMMUNE_KEYWORDS)),
                "source": source.get("source", "GOA GAF"),
                "source_version": source.get("source_version", "unknown"),
            }
        )
    return pd.DataFrame(rows)


def _bundled_small_fixture_frame(config: dict[str, Any]) -> pd.DataFrame:
    source = config["source"]
    return pd.DataFrame(
        {
            "gene_symbol": ["A1BG", "IFIT1", "STAT1", "MISSING_FIXTURE_GENE"],
            "approved_symbol_present": [1, 1, 1, 0],
            "gene_biotype": [
                "protein-coding gene",
                "protein-coding gene",
                "protein-coding gene",
                "unknown",
            ],
            "locus_group": [
                "protein-coding gene",
                "protein-coding gene",
                "protein-coding gene",
                "unknown",
            ],
            "hgnc_gene_group_count": [0, 1, 1, 0],
            "go_annotation_count": [1, 12, 10, 0],
            "go_bp_count": [0, 8, 7, 0],
            "go_mf_count": [1, 2, 1, 0],
            "go_cc_count": [0, 2, 2, 0],
            "is_immune_related": [0, 1, 1, 0],
            "source": source.get("source", "bundled_small_fixture"),
            "source_version": source.get("source_version", "test-fixture"),
        }
    )


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
    if source_mode in {
        "local_csv",
        "local_curated_gene_prior_csv",
        "hgnc_local_tsv",
        "goa_local_gaf",
    }:
        source = config["source"].get("path", "missing path")
    elif source_mode == "synthetic_gene_prior":
        source = config["source"].get("data_config", "synthetic gene list")
    elif source_mode == "download_hgnc":
        source = config["source"].get("url", DEFAULT_HGNC_URL)
    elif source_mode == "download_goa":
        source = config["source"].get("url", DEFAULT_GOA_HUMAN_URL)
    elif source_mode == "bundled_small_fixture":
        source = "bundled small test fixture"
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


def _resolve_output_dir(config: dict[str, Any]) -> Path:
    output_dir = Path(config["output_root"]) / config["prior_id"]
    output_subdir = config.get("output_subdir") or config["source"].get("output_subdir")
    if output_subdir:
        output_dir = output_dir / str(output_subdir)
    return output_dir


def _download_source_file(config: dict[str, Any], *, url: str, filename: str) -> Path:
    source = config["source"]
    cache_dir = Path(source.get("cache_dir", "data/interim/gene_priors/_source_cache"))
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / filename
    try:
        with urlopen(url, timeout=int(source.get("timeout_seconds", 60))) as response:
            path.write_bytes(response.read())
    except (URLError, OSError, TimeoutError) as exc:
        raise RuntimeError(
            f"could not download gene-prior source from {url}; "
            "provide a local source path instead"
        ) from exc
    expected_sha256 = source.get("expected_sha256")
    if expected_sha256 and _sha256sum(path).lower() != str(expected_sha256).lower():
        raise RuntimeError(f"downloaded source checksum mismatch for {url}")
    return path


def _source_file_record(
    path: Path,
    *,
    role: str,
    url: str | None = None,
) -> dict[str, str | None]:
    return {
        "role": role,
        "path": str(path),
        "url": url,
        "md5": md5sum(path) if path.exists() else None,
        "sha256": _sha256sum(path) if path.exists() else None,
    }


def _sha256sum(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _first_existing(frame: pd.DataFrame, candidates: tuple[str, ...]) -> str:
    for candidate in candidates:
        if candidate in frame.columns:
            return candidate
    raise ValueError(f"source is missing required columns; tried {', '.join(candidates)}")


def _clean_scalar(value: Any) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def _pipe_count(value: str) -> int:
    if not value:
        return 0
    return len([part for part in str(value).split("|") if part.strip()])


def _source_is_real_for_config(config: dict[str, Any]) -> bool:
    mode = config["source"]["mode"]
    if mode in {"synthetic_gene_prior", "bundled_small_fixture"}:
        return False
    return bool(config["source"].get("source_is_real", True))


def _source_kind_for_config(config: dict[str, Any]) -> str:
    mode = config["source"]["mode"]
    if mode in {"synthetic_gene_prior"}:
        return "synthetic_placeholder"
    if mode == "bundled_small_fixture":
        return "test_fixture"
    if mode in {"hgnc_local_tsv", "download_hgnc"}:
        return "real_functional_gene_metadata"
    if mode in {"goa_local_gaf", "download_goa"}:
        return "real_functional_go_annotation"
    return config["source"].get("source_kind", "local_curated_gene_prior")


def _git_commit() -> str:
    import subprocess

    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"
