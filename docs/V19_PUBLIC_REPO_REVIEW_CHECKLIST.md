# v0.19 Public Repo Review Checklist

## Reviewer Entry Points

- README first screen explains result, claim boundary, quickstart, and file map.
- Model card: `docs/V18_RELEASE_MODEL_CARD.md`
- Benchmark card: `docs/V18_BENCHMARK_CARD.md`
- Reproducibility runbook: `docs/V18_REPRODUCIBILITY_RUNBOOK.md`
- External review index: `docs/V18_EXTERNAL_REVIEW_INDEX.md`
- Portfolio summary: `docs/V19_APPLICATION_PORTFOLIO_SUMMARY.md`

## Reproducibility

- Data checksum: `c870e6967d91c017d9da827bab183cd6`
- Split manifest: `outputs/runs/v0.17-norman-validated-residual-baseline/gears_norman_scperturb_v013/20260625T100322Z/split_manifest.csv`
- Config: `configs/experiment/gears_norman_v017_multiseed_residual.yaml`
- Command: `python scripts/run_norman_residual_multiseed.py --config configs/experiment/gears_norman_v017_multiseed_residual.yaml`
- Seeds: `0, 1, 2, 3, 4`
- Metrics file: `aggregate_metrics.csv`

## Smoke And Integrity Commands

```powershell
python scripts/run_release_smoke.py --config configs/experiment/release_smoke_v019.yaml
python scripts/diagnose_official_gears.py
python scripts/check_release_artifacts.py
```

Latest local artifacts:

- smoke: `outputs/runs/v0.19-release-smoke/20260625T223712Z/`, status `pass`;
- GEARS diagnostic: `outputs/runs/v0.19-official-gears-diagnostics/20260625T223710Z/`, status `import_ok_run_blocked`;
- artifact manifest: `reports/v0.19_artifact_manifest.md`, status `pass`.

## Repository Hygiene

- Raw data is ignored and must not be committed.
- `outputs/` are ignored and must not be committed.
- `.venv/`, `.venv_gears/`, caches, and temporary directories are ignored.
- License is intentionally marked pending until the project owner selects a license.

## Claim Boundary

Allowed: reproducible validated residual baseline on the fixed internal GEARS-compatible Norman split.

Forbidden: official GEARS, leaderboard comparability, SOTA, biological discovery, or broad model superiority.
