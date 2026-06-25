from pathlib import Path

import yaml


def test_gears_norman_config_locks_public_source():
    config = _load_yaml(Path("configs/data/gears_norman_v013.yaml"))
    dataset = config["data"]["dataset"]

    assert config["benchmark"]["benchmark_id"] == "gears_norman_scperturb_v013"
    assert dataset["expected_raw_path"].endswith("NormanWeissman2019_filtered.h5ad")
    assert dataset["checksum"] == "c870e6967d91c017d9da827bab183cd6"
    assert int(dataset["file_size_bytes"]) < 2 * 1024 * 1024 * 1024


def test_gears_norman_v014_configs_lock_alignment_status():
    aligned = _load_yaml(Path("configs/experiment/gears_norman_v014_aligned_baseline.yaml"))
    wrapper = _load_yaml(Path("configs/experiment/gears_norman_v014_official_wrapper.yaml"))

    assert aligned["output_prefix"] == "v0.14-gears-aligned-baseline"
    assert aligned["split"]["random_combo_fraction"] > 0
    assert any(item["name"] == "weighted_combo_additive" for item in aligned["baselines"])
    assert wrapper["benchmark"]["official_alignment_status"] == "official_wrapper_blocked"


def test_gears_norman_v015_config_locks_fast_neural_scope():
    config = _load_yaml(Path("configs/experiment/gears_norman_v015_fast_neural.yaml"))

    assert config["output_prefix"] == "v0.15-fast-neural-norman-baseline"
    assert config["benchmark"]["official_alignment_status"] == (
        "gears_compatible_internal_neural_baseline"
    )
    assert config["model"]["backend"] == "sklearn_mlp_regressor_pca"
    assert len(config["model"]["seeds"]) == 3
    assert config["split"]["seed"] == 1400
    assert "not official GEARS" in config["reporting"]["claim_boundary"]


def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    return payload if isinstance(payload, dict) else {}
