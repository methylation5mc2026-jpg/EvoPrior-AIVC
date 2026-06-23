from pathlib import Path

import pytest

from evoprior_aivc.data.download import prepare_dataset
from evoprior_aivc.data.registry import DatasetRecord, resolve_local_path


def test_dataset_record_from_config_and_dry_run(tmp_path):
    config = _config(tmp_path)

    record = DatasetRecord.from_config(config)
    result = prepare_dataset(config, dry_run=True)

    assert record.dataset_id == "toy_real"
    assert resolve_local_path(record, config) == tmp_path / "toy.h5ad"
    assert result.status == "dry_run"
    assert "toy_real" in result.message


def test_prepare_dataset_accepts_existing_local_file_without_checksum(tmp_path):
    config = _config(tmp_path, checksum="checksum unavailable")
    path = tmp_path / "toy.h5ad"
    path.write_text("fake", encoding="utf-8")

    result = prepare_dataset(config)

    assert result.status == "ready"
    assert result.downloaded is False
    assert result.checksum_status == "checksum unavailable"


def test_prepare_dataset_rejects_missing_manual_file(tmp_path):
    config = _config(tmp_path)
    config["prepare"]["mode"] = "manual"

    with pytest.raises(FileNotFoundError, match="Dataset file not found"):
        prepare_dataset(config)


def _config(tmp_path: Path, checksum: str = ""):
    return {
        "dataset": {
            "dataset_id": "toy_real",
            "display_name": "Toy real",
            "source_url": None,
            "expected_raw_path": str(tmp_path / "toy.h5ad"),
            "expected_format": "h5ad",
            "checksum": checksum,
            "checksum_algorithm": "md5" if checksum else None,
            "license": "test",
            "access_notes": "test only",
            "adapter": "generic_h5ad",
            "allow_auto_download": False,
            "manual_download_note": "place toy.h5ad",
        },
        "prepare": {"mode": "local_or_download", "local_path": None},
    }

