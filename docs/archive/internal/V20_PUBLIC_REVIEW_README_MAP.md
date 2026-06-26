# v0.20 Public Review README Map

## Start Here

1. `README.md` for the project summary, key result table, no-data review path, and with-data reproduction path.
2. `docs/V18_EXTERNAL_REVIEW_INDEX.md` for the v0.17/v0.18 external review package.
3. `docs/V20_RELEASE_CHECKLIST.md` for release readiness.
4. `docs/V20_OFFICIAL_GEARS_DOCKER_ENV.md` for the official GEARS unblock route.

## No-Data Review Path

```powershell
python -m pip install -e ".[dev]"
python -m pytest -p no:cacheprovider --basetemp .tmp_pytest_local tests/test_release_smoke_config.py tests/test_release_artifact_manifest.py tests/test_official_gears_diagnostics.py
python scripts/run_release_smoke.py --config configs/experiment/release_smoke_v019.yaml
python scripts/make_release_bundle.py --config configs/release/v020_release_bundle.yaml
```

Read:

- `docs/V18_RELEASE_MODEL_CARD.md`
- `docs/V18_BENCHMARK_CARD.md`
- `docs/V18_REPRODUCIBILITY_RUNBOOK.md`
- `reports/v0.19_application_portfolio_summary.md`

## With-Local-Data Reproduction Path

Place the Norman/scPerturb file at:

```text
data/raw/NormanWeissman2019_filtered.h5ad
```

Expected md5:

```text
c870e6967d91c017d9da827bab183cd6
```

Run:

```powershell
python scripts/prepare_gears_norman.py --config configs/data/gears_norman_v013.yaml --dry-run
python scripts/run_norman_residual_multiseed.py --config configs/experiment/gears_norman_v017_multiseed_residual.yaml
python scripts/check_release_artifacts.py
```

## Evidence Pointers

- Config: `configs/experiment/gears_norman_v017_multiseed_residual.yaml`
- Split manifest: `outputs/runs/v0.17-norman-validated-residual-baseline/gears_norman_scperturb_v013/20260625T100322Z/split_manifest.csv`
- Primary output: `outputs/runs/v0.17-norman-validated-residual-baseline/gears_norman_scperturb_v013/20260625T100322Z/`
- Smoke result: `outputs/runs/v0.19-release-smoke/20260625T230440Z/`
- Artifact manifest: `reports/v0.20_artifact_manifest.md`

## Claim Boundary

This map supports review and reproduction. It does not establish official GEARS, leaderboard comparability, SOTA, biological discovery, or broad model superiority.
