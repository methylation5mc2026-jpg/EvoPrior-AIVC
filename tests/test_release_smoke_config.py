import importlib
from pathlib import Path

import yaml


def test_release_smoke_config_points_to_review_artifacts():
    config = _load_yaml(Path("configs/experiment/release_smoke_v019.yaml"))

    assert config["output_prefix"] == "v0.19-release-smoke"
    assert config["data"]["checksum_md5"] == "c870e6967d91c017d9da827bab183cd6"
    assert "docs/V18_RELEASE_MODEL_CARD.md" in config["release"]["required_docs"]
    assert "scripts/run_norman_residual_multiseed.py" in config["release"]["required_scripts"]
    assert config["release"]["pytest_subset"]


def test_tiny_residual_smoke_fixture_passes():
    module = importlib.import_module("scripts.run_release_smoke")

    check = module._check_tiny_residual_baseline()

    assert check.status == "pass"


def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    return payload if isinstance(payload, dict) else {}
