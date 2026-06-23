"""Dataset registry records for real perturbation data."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class DatasetRecord:
    """Minimal metadata needed to locate and adapt a dataset."""

    dataset_id: str
    display_name: str
    source_url: str | None
    expected_raw_path: Path
    expected_format: str
    checksum: str | None
    checksum_algorithm: str | None
    license: str
    access_notes: str
    adapter: str
    file_size_bytes: int | None = None
    manual_download_note: str | None = None
    allow_auto_download: bool = False

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "DatasetRecord":
        dataset = config["dataset"]
        checksum = dataset.get("checksum")
        checksum_algorithm = dataset.get("checksum_algorithm")
        if checksum in {None, "", "checksum unavailable"}:
            checksum = None
            checksum_algorithm = None
        return cls(
            dataset_id=dataset["dataset_id"],
            display_name=dataset["display_name"],
            source_url=dataset.get("source_url"),
            expected_raw_path=Path(dataset["expected_raw_path"]),
            expected_format=dataset["expected_format"],
            checksum=checksum,
            checksum_algorithm=checksum_algorithm,
            license=dataset.get("license", "unknown"),
            access_notes=dataset.get("access_notes", ""),
            adapter=dataset["adapter"],
            file_size_bytes=dataset.get("file_size_bytes"),
            manual_download_note=dataset.get("manual_download_note"),
            allow_auto_download=bool(dataset.get("allow_auto_download", False)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "display_name": self.display_name,
            "source_url": self.source_url,
            "expected_raw_path": str(self.expected_raw_path),
            "expected_format": self.expected_format,
            "checksum": self.checksum or "checksum unavailable",
            "checksum_algorithm": self.checksum_algorithm or "none",
            "license": self.license,
            "access_notes": self.access_notes,
            "adapter": self.adapter,
            "file_size_bytes": self.file_size_bytes,
            "manual_download_note": self.manual_download_note,
            "allow_auto_download": self.allow_auto_download,
        }


def resolve_local_path(record: DatasetRecord, config: dict[str, Any]) -> Path:
    """Resolve a local override path or the registry raw path."""
    local_path = config.get("prepare", {}).get("local_path")
    if local_path:
        return Path(local_path)
    return record.expected_raw_path

