from pathlib import Path

import yaml


def test_gears_norman_config_locks_public_source():
    config = _load_yaml(Path("configs/data/gears_norman_v013.yaml"))
    dataset = config["data"]["dataset"]

    assert config["benchmark"]["benchmark_id"] == "gears_norman_scperturb_v013"
    assert dataset["expected_raw_path"].endswith("NormanWeissman2019_filtered.h5ad")
    assert dataset["checksum"] == "c870e6967d91c017d9da827bab183cd6"
    assert int(dataset["file_size_bytes"]) < 2 * 1024 * 1024 * 1024


def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    return payload if isinstance(payload, dict) else {}
