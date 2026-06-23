"""Dataset preparation helpers with dry-run, local, manual, and download modes."""

from __future__ import annotations

import hashlib
import shutil
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from evoprior_aivc.data.registry import DatasetRecord, resolve_local_path


@dataclass(frozen=True)
class DatasetPreparationResult:
    """Result of preparing or planning a dataset file."""

    dataset_id: str
    path: Path
    status: str
    downloaded: bool
    checksum_status: str
    message: str

    def to_dict(self) -> dict[str, str | bool]:
        return {
            "dataset_id": self.dataset_id,
            "path": str(self.path),
            "status": self.status,
            "downloaded": self.downloaded,
            "checksum_status": self.checksum_status,
            "message": self.message,
        }


def prepare_dataset(
    config: dict[str, Any],
    *,
    dry_run: bool = False,
) -> DatasetPreparationResult:
    """Prepare a dataset according to registry config."""
    record = DatasetRecord.from_config(config)
    path = resolve_local_path(record, config)
    mode = config.get("prepare", {}).get("mode", "local_or_download")

    if dry_run:
        message = _plan_message(record, path, mode)
        return DatasetPreparationResult(
            dataset_id=record.dataset_id,
            path=path,
            status="dry_run",
            downloaded=False,
            checksum_status="not_checked",
            message=message,
        )

    if path.exists():
        checksum_status = verify_checksum(path, record)
        return DatasetPreparationResult(
            dataset_id=record.dataset_id,
            path=path,
            status="ready",
            downloaded=False,
            checksum_status=checksum_status,
            message=f"Using existing dataset file: {path}",
        )

    if mode == "manual" or not record.allow_auto_download or not record.source_url:
        note = record.manual_download_note or "Place the dataset file at the expected raw path."
        raise FileNotFoundError(f"Dataset file not found at {path}. {note}")

    if mode not in {"local_or_download", "download"}:
        raise ValueError("prepare.mode must be one of: local_or_download, download, manual")

    path.parent.mkdir(parents=True, exist_ok=True)
    _download_file(record.source_url, path)
    checksum_status = verify_checksum(path, record)
    return DatasetPreparationResult(
        dataset_id=record.dataset_id,
        path=path,
        status="ready",
        downloaded=True,
        checksum_status=checksum_status,
        message=f"Downloaded dataset file to: {path}",
    )


def verify_checksum(path: Path, record: DatasetRecord) -> str:
    """Return checksum status and raise on mismatch."""
    if record.checksum is None:
        return "checksum unavailable"
    if record.checksum_algorithm != "md5":
        raise ValueError(f"unsupported checksum algorithm: {record.checksum_algorithm}")
    observed = md5sum(path)
    if observed != record.checksum:
        raise ValueError(
            f"checksum mismatch for {path}: expected {record.checksum}, observed {observed}"
        )
    return "ok"


def md5sum(path: Path, *, chunk_size: int = 1024 * 1024) -> str:
    """Compute an md5 checksum for a local file."""
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _download_file(url: str, path: Path) -> None:
    temp_path = path.with_suffix(path.suffix + ".tmp")
    try:
        with urllib.request.urlopen(url) as response, temp_path.open("wb") as handle:
            shutil.copyfileobj(response, handle)
        temp_path.replace(path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def _plan_message(record: DatasetRecord, path: Path, mode: str) -> str:
    source = record.source_url or "manual download only"
    checksum = record.checksum or "checksum unavailable"
    return (
        f"dataset_id={record.dataset_id}; mode={mode}; expected_path={path}; "
        f"source={source}; checksum={checksum}; allow_auto_download={record.allow_auto_download}"
    )

