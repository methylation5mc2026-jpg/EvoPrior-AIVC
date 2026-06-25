from pathlib import Path

import yaml

from scripts.make_release_bundle import build_manifest, build_release_bundle


def test_release_bundle_manifest_tracks_claim_boundary():
    config = _load_yaml(Path("configs/release/v020_release_bundle.yaml"))
    manifest = build_manifest(config)

    assert manifest["release_id"] == "v0.20-github-release-or-official-gears-docker-env"
    assert manifest["dataset_md5"] == "c870e6967d91c017d9da827bab183cd6"
    assert "Official GEARS result." in manifest["claim_boundary"]["forbidden"]
    assert all(not item["path"].startswith("data/raw/") for item in manifest["reference_files"])


def test_release_bundle_writes_required_files(tmp_path):
    config = _load_yaml(Path("configs/release/v020_release_bundle.yaml"))
    config["output_root"] = str(tmp_path / "release")
    config["include_zip"] = True

    bundle_dir = build_release_bundle(config)

    assert (bundle_dir / "release_manifest.json").exists()
    assert (bundle_dir / "release_manifest.md").exists()
    assert (bundle_dir / "README_snapshot.md").exists()
    assert (bundle_dir / "key_metrics_summary.md").exists()
    assert (bundle_dir / "claim_boundary.md").exists()
    assert (bundle_dir / "reproduction_commands.md").exists()
    assert (bundle_dir / "file_index.md").exists()
    assert any(path.name.endswith("_review_bundle.zip") for path in bundle_dir.iterdir())


def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    return payload if isinstance(payload, dict) else {}
