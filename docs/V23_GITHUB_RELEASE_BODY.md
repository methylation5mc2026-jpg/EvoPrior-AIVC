# EvoPrior-AIVC v0.23 Public Review Package

## Summary

This release packages EvoPrior-AIVC for GitHub publication, personal-site linking, and fast mentor review. The scientific result remains the v0.17 validated residual baseline on a public Norman/scPerturb GEARS-compatible internal split.

## Main Validated Result

Dataset: `NormanWeissman2019_filtered.h5ad`

Checksum: `c870e6967d91c017d9da827bab183cd6`

Split status: fixed internal GEARS-compatible seen0/seen1/seen2/random_combo split; not official GEARS.

Primary command:

```powershell
python scripts/run_norman_residual_multiseed.py --config configs/experiment/gears_norman_v017_multiseed_residual.yaml
```

Reference output:

```text
outputs/runs/v0.17-norman-validated-residual-baseline/gears_norman_scperturb_v013/20260625T100322Z/
```

| model | seeds | MAE | MSE | Pearson delta | Spearman logFC |
| --- | ---: | ---: | ---: | ---: | ---: |
| v0.14 weighted combo additive | 1 | 0.5660 | 6.6759 | 0.7599 | 0.6390 |
| v0.15 fast MLP/PCA | 3 | 0.5877 | 7.5517 | 0.7134 | 0.6317 |
| v0.17 validated residual baseline | 5 | 0.430778 | 3.668870 | 0.869224 | 0.784976 |

## What Is Included

- Public README and review map.
- GitHub publish guide.
- Project-page copy and showcase assets.
- Mentor review brief.
- Model card, benchmark card, runbook, and external result card.
- No-data smoke path and with-data reproduction path.
- Sanitization and final publication checklist.

## Reproduction Paths

No-data review:

```powershell
python -m pip install -e ".[dev]"
python -m pytest -p no:cacheprovider --basetemp .tmp_pytest_local tests/test_release_smoke_config.py tests/test_release_artifact_manifest.py tests/test_official_gears_diagnostics.py tests/test_ci_workflow_static.py
python scripts/check_ci_workflow.py --workflow .github/workflows/ci.yml
python scripts/run_release_smoke.py --config configs/experiment/release_smoke_v019.yaml
python scripts/check_release_artifacts.py
```

With local data:

```powershell
python scripts/prepare_gears_norman.py --config configs/data/gears_norman_v013.yaml --dry-run
python scripts/run_norman_residual_multiseed.py --config configs/experiment/gears_norman_v017_multiseed_residual.yaml
python scripts/check_release_artifacts.py
```

## Data Requirement

Place the Norman/scPerturb H5AD at:

```text
data/raw/NormanWeissman2019_filtered.h5ad
```

Expected md5:

```text
c870e6967d91c017d9da827bab183cd6
```

Raw data is not included in the repository.

## Claim Boundary

Allowed: reproducible public review package and a validated project-owned residual baseline under one documented internal GEARS-compatible Norman split.

Not claimed: official GEARS, leaderboard comparability, SOTA, biological discovery, clinical use, or broad model superiority.

## Known Limitations

- The split is GEARS-compatible/internal, not official GEARS.
- Metrics are internal compatible metrics.
- Docker and official GEARS execution remain blocked unless a reviewer supplies a working environment and exact official split/metric alignment.
- The v0.23 milestone is publication preparation only; it does not add a new performance result.

## Recommended Review Order

1. `README.md`
2. `docs/V23_SHOWCASE_INDEX.md`
3. `docs/V18_RELEASE_MODEL_CARD.md`
4. `docs/V18_BENCHMARK_CARD.md`
5. `docs/V17_EXTERNAL_RESULT_CARD.md`
6. `docs/V22_PUBLIC_DEMO_GUIDE.md`
7. `docs/V23_MENTOR_REVIEW_BRIEF.md`

## Next Steps

Publish to GitHub, create a release from tag `v0.23-github-publish-or-project-page-assets`, then optionally integrate the project card into a personal website.
