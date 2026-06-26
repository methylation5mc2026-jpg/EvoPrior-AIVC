from scripts.check_release_artifacts import build_manifest


def test_release_artifact_manifest_tracks_required_release_docs():
    manifest = build_manifest()
    required_paths = {item["path"] for item in manifest["required_files"]}

    assert "docs/V18_RELEASE_MODEL_CARD.md" in required_paths
    assert "docs/V19_PUBLIC_REPO_REVIEW_CHECKLIST.md" in required_paths
    assert "docs/V20_GITHUB_RELEASE_PLAN.md" in required_paths
    assert "docs/V21_RELEASE_CANDIDATE_PLAN.md" in required_paths
    assert "docs/V21_DOCKER_GEARS_TEST_REPORT.md" in required_paths
    assert "docs/V21_CI_VALIDATION_REPORT.md" in required_paths
    assert "docs/V22_PUBLIC_GITHUB_FINAL_CHECK.md" in required_paths
    assert "docs/V22_REPO_SANITIZATION_REPORT.md" in required_paths
    assert "docs/V22_GITHUB_RELEASE_NOTES_FINAL.md" in required_paths
    assert "docs/V22_GITHUB_REPO_PROFILE.md" in required_paths
    assert "docs/V22_PUBLIC_DEMO_GUIDE.md" in required_paths
    assert "docs/V23_GITHUB_PUBLISH_GUIDE.md" in required_paths
    assert "docs/V23_PROJECT_PAGE_ASSETS.md" in required_paths
    assert "docs/V24_GITHUB_PUBLISH_STATUS.md" in required_paths
    assert "docs/V24_GITHUB_RELEASE_DRAFT.md" in required_paths
    assert "docs/V24_GITHUB_PUBLISH_COMMANDS.md" in required_paths
    assert "docs/V24_WEBSITE_INTEGRATION_ASSETS.md" in required_paths
    assert "docs/V24_PUBLIC_LINK_AUDIT.md" in required_paths
    assert "docs/V24_FINAL_PRESENTATION_SUMMARY.md" in required_paths
    assert "scripts/check_ci_workflow.py" in required_paths
    assert ".github/workflows/ci.yml" in required_paths
    assert "docker/Dockerfile.gears" in required_paths
    assert manifest["dataset_md5"] == "c870e6967d91c017d9da827bab183cd6"
    assert manifest["git_tag_expected"] == "v0.24-github-push-and-release-or-website-integration"
    assert manifest["rollback_tag"] == "v0.23-github-publish-or-project-page-assets"
    assert all(not path.startswith("data/raw/") for path in manifest["staged_files_checked"])
