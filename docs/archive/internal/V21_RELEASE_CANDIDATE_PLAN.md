# v0.21 Release Candidate Plan

## Objective

Turn the v0.20 release-ready package into a reviewer-facing release candidate by validating the Docker/GEARS path, validating CI assumptions, documenting public data acquisition, refreshing the release bundle, and writing release notes.

## Rollback

`v0.20-github-release-or-official-gears-docker-env`

## Required Evidence

- Commit/tag: pending until v0.21 commit and tag.
- Smoke command: `python scripts/run_release_smoke.py --config configs/experiment/release_smoke_v019.yaml`
- Smoke output: `outputs/runs/v0.19-release-smoke/20260625T233315Z/`, status `pass`
- Artifact checker: `python scripts/check_release_artifacts.py`
- Artifact output: `reports/v0.21_artifact_manifest.json`, status `pass`
- Release bundle command: `python scripts/make_release_bundle.py --config configs/release/v021_release_bundle.yaml`
- Release bundle output: `outputs/release/v0.21/20260625T233703Z/`
- Dataset checksum: `c870e6967d91c017d9da827bab183cd6`
- Benchmark output: `outputs/runs/v0.17-norman-validated-residual-baseline/gears_norman_scperturb_v013/20260625T100322Z/`
- Docker/GEARS diagnostic: `docs/V21_DOCKER_GEARS_TEST_REPORT.md`
- Official GEARS diagnostic output: `outputs/runs/v0.20-official-gears-diagnostics/20260625T233312Z/`, status `import_ok_run_blocked`
- CI validation: `python scripts/check_ci_workflow.py --workflow .github/workflows/ci.yml`, status `pass`

## Decision

v0.21 is a release candidate if tests pass, artifact checker passes, the release bundle is generated, Docker availability is honestly reported, CI validation is documented, and no raw data or large generated outputs are staged.

## Claim Boundary

This milestone is release engineering. It does not change the v0.17 benchmark result, does not run official GEARS, and does not claim SOTA or leaderboard comparability.
