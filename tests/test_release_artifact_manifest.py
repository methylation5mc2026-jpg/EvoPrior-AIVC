from scripts.check_release_artifacts import build_manifest


def test_release_artifact_manifest_tracks_required_release_docs():
    manifest = build_manifest()
    required_paths = {item["path"] for item in manifest["required_files"]}

    assert "docs/V18_RELEASE_MODEL_CARD.md" in required_paths
    assert "docs/V19_PUBLIC_REPO_REVIEW_CHECKLIST.md" in required_paths
    assert manifest["dataset_md5"] == "c870e6967d91c017d9da827bab183cd6"
    assert all(not path.startswith("data/raw/") for path in manifest["staged_files_checked"])
