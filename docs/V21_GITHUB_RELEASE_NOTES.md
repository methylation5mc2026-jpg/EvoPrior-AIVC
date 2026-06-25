# EvoPrior-AIVC v0.21 Release Candidate

## What Is Included

- GitHub no-data CI smoke workflow.
- Release candidate bundle generator and v0.21 bundle config.
- Public Norman/scPerturb data acquisition guide.
- Static CI validation report.
- Docker/GEARS environment test report.
- Artifact integrity manifest.
- Reviewer-facing release notes.

## Local v0.21 Evidence

- Release bundle: `outputs/release/v0.21/20260625T233703Z/`
- Release smoke: `outputs/runs/v0.19-release-smoke/20260625T233315Z/`, status `pass`
- Official GEARS diagnostic: `outputs/runs/v0.20-official-gears-diagnostics/20260625T233312Z/`, status `import_ok_run_blocked`
- Artifact manifest: `reports/v0.21_artifact_manifest.md`, status `pass`
- Static CI validation: `python scripts/check_ci_workflow.py --workflow .github/workflows/ci.yml`, status `pass`

## Main Validated Result

The main benchmark evidence remains the v0.17 residual baseline on the public Norman/scPerturb GEARS-compatible internal split:

- MAE: `0.430778`
- MSE: `3.668870`
- Pearson delta: `0.869224`
- Spearman delta: `0.784976`
- Seeds: `0, 1, 2, 3, 4`
- Output: `outputs/runs/v0.17-norman-validated-residual-baseline/gears_norman_scperturb_v013/20260625T100322Z/`
- Dataset md5: `c870e6967d91c017d9da827bab183cd6`

## How To Reproduce

No-data review:

```powershell
python -m pip install -e ".[dev]"
python -m pytest -p no:cacheprovider --basetemp .tmp_pytest_local tests/test_release_smoke_config.py tests/test_release_artifact_manifest.py tests/test_official_gears_diagnostics.py tests/test_ci_workflow_static.py
python scripts/check_ci_workflow.py --workflow .github/workflows/ci.yml
python scripts/run_release_smoke.py --config configs/experiment/release_smoke_v019.yaml
```

With local data:

```powershell
python scripts/prepare_gears_norman.py --config configs/data/gears_norman_v013.yaml --dry-run
python scripts/run_norman_residual_multiseed.py --config configs/experiment/gears_norman_v017_multiseed_residual.yaml
python scripts/check_release_artifacts.py
```

## What Is Not Claimed

- Not official GEARS.
- Not leaderboard comparable.
- Not SOTA.
- Not a biological discovery.
- Not broad model superiority.

## Official GEARS Status

Docker is unavailable in this local environment, so the v0.21 Docker/GEARS status is `unavailable_docker`. The Dockerfile remains an environment route, not a completed official GEARS run.

## Known Limitations

- The split is internal GEARS-compatible, not official GEARS.
- The metrics are internal compatible metrics.
- GitHub Actions was statically validated locally but not executed by this environment.
- Docker build/import was blocked because Docker is not installed or not on PATH.

## Recommended Review Path

1. Read `README.md`.
2. Read `docs/V18_RELEASE_MODEL_CARD.md`.
3. Read `docs/V18_BENCHMARK_CARD.md`.
4. Read `docs/V21_PUBLIC_DATA_ACQUISITION_GUIDE.md`.
5. Run the no-data review commands.

## Next Milestone

`v0.22-github-release-finalization-or-official-gears-container-run`
