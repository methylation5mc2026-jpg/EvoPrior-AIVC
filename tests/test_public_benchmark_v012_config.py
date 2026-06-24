from pathlib import Path

import yaml


def test_public_benchmark_v012_data_config_locks_source_and_checksum():
    config = _load_yaml(Path("configs/data/public_benchmark_v012.yaml"))
    dataset = config["data"]["dataset"]

    assert config["benchmark"]["benchmark_id"] == "scperturb_papalexi_2021_arrayed_rna_v012"
    assert dataset["expected_raw_path"].endswith("PapalexiSatija2021_eccite_arrayed_RNA.h5ad")
    assert dataset["checksum"] == "843820d48b024348d6132cd53be0da91"
    assert int(dataset["file_size_bytes"]) < 2 * 1024 * 1024 * 1024


def test_public_benchmark_v012_experiment_has_required_baselines():
    config = _load_yaml(Path("configs/experiment/public_benchmark_v012_baseline.yaml"))
    baselines = {item["name"] for item in config["baselines"]}

    assert {
        "no_change",
        "control_mean",
        "mean_delta",
        "ridge_cv",
        "evoprior_additive_no_prior",
    }.issubset(baselines)
    assert config["benchmark"]["official_alignment_status"] == "custom_benchmark_compatible"


def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    return payload if isinstance(payload, dict) else {}
