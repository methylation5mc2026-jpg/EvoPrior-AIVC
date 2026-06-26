# v0.20 Release Checklist

## 1. Repo Hygiene

- `git status --short` reviewed before commit.
- Raw data, outputs, virtual environments, Docker build cache, and test caches are not staged.
- Release bundle outputs stay under ignored `outputs/release/`.

## 2. Data Policy

- Raw Norman data is not committed.
- Expected local path: `data/raw/NormanWeissman2019_filtered.h5ad`
- Expected md5: `c870e6967d91c017d9da827bab183cd6`

## 3. Claim Boundary

Allowed: GitHub/release readiness and reproducibility packaging over the v0.17 validated residual baseline.

Forbidden: official GEARS, leaderboard comparability, SOTA, biological discovery, or broad model superiority.

## 4. Benchmark Reproducibility

- Config: `configs/experiment/gears_norman_v017_multiseed_residual.yaml`
- Command: `python scripts/run_norman_residual_multiseed.py --config configs/experiment/gears_norman_v017_multiseed_residual.yaml`
- Primary output: `outputs/runs/v0.17-norman-validated-residual-baseline/gears_norman_scperturb_v013/20260625T100322Z/`
- Smoke command: `python scripts/run_release_smoke.py --config configs/experiment/release_smoke_v019.yaml`

## 5. CI Smoke

- Workflow: `.github/workflows/ci.yml`
- No-data tests: `tests/test_release_smoke_config.py`, `tests/test_release_artifact_manifest.py`, `tests/test_official_gears_diagnostics.py`
- No-data smoke: `python scripts/run_release_smoke.py --config configs/experiment/release_smoke_v019.yaml`

## 6. Official GEARS Status

- Diagnostic: `python scripts/diagnose_official_gears.py`
- Docker route: `docker/Dockerfile.gears`
- Latest diagnostic output: `outputs/runs/v0.20-official-gears-diagnostics/20260625T230451Z/`
- Status remains blocked until official train/evaluate, official split, and official metrics are implemented.

## 7. Known Limitations

- Internal GEARS-compatible split only.
- Internal compatible metrics only.
- Single Norman/scPerturb public dataset context.
- Dockerfile is a route, not a claimed tested official reproduction unless separately run.

## 8. What To Show To Mentor

- `README.md`
- `docs/V18_RELEASE_MODEL_CARD.md`
- `docs/V18_BENCHMARK_CARD.md`
- `docs/V18_EXTERNAL_REVIEW_INDEX.md`
- `docs/V20_PUBLIC_REVIEW_README_MAP.md`
- `reports/v0.19_application_portfolio_summary.md`

## 9. What Not To Claim

- Do not claim official GEARS.
- Do not claim SOTA.
- Do not claim leaderboard comparability.
- Do not claim biological discovery.
- Do not claim general model superiority.
