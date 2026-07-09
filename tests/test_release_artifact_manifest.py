from scripts import check_release_artifacts

build_manifest = check_release_artifacts.build_manifest


def test_release_artifact_manifest_tracks_required_release_docs():
    manifest = build_manifest()
    required_paths = {item["path"] for item in manifest["required_files"]}

    assert "docs/MODEL_CARD.md" in required_paths
    assert "docs/BENCHMARK_CARD.md" in required_paths
    assert "docs/REPRODUCIBILITY.md" in required_paths
    assert "docs/DATA.md" in required_paths
    assert "docs/KNOWN_LIMITATIONS.md" in required_paths
    assert "docs/EXPERIMENT_LEDGER.md" in required_paths
    assert "docs/CLAIMS_AND_EVIDENCE.md" in required_paths
    assert "docs/V21_DOCKER_GEARS_TEST_REPORT.md" in required_paths
    assert "docs/V21_CI_VALIDATION_REPORT.md" in required_paths
    archived_prefixes = ("docs/" + "V" + "23_", "docs/" + "V" + "24_GITHUB_")
    assert all(not path.startswith(archived_prefixes) for path in required_paths)
    assert "scripts/check_ci_workflow.py" in required_paths
    assert ".github/workflows/ci.yml" in required_paths
    assert "docker/Dockerfile.gears" in required_paths
    assert manifest["dataset_md5"] == "c870e6967d91c017d9da827bab183cd6"
    assert manifest["git_tag_expected"] == "public-technical-package"
    assert manifest["rollback_tag"] == "v0.26-main-merge-release-and-public-verification"
    assert all(not path.startswith("data/raw/") for path in manifest["staged_files_checked"])


def test_release_artifact_check_does_not_rewrite_historical_reports(
    tmp_path, monkeypatch, capsys
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        check_release_artifacts,
        "build_manifest",
        lambda: {"release_id": "public-technical-package", "status": "pass"},
    )

    check_release_artifacts.main()

    assert not (tmp_path / "reports").exists()
    assert capsys.readouterr().out.splitlines() == ["public-technical-package", "pass"]
