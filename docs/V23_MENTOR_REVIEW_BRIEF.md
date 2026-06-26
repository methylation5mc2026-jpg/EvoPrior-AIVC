# v0.23 Mentor Review Brief

## Problem

Single-cell perturbation-response prediction needs careful benchmark discipline: public data, fixed splits, leakage checks, baseline comparisons, and honest claims.

## Data And Benchmark

- Dataset: Norman/scPerturb `NormanWeissman2019_filtered.h5ad`
- Checksum: `c870e6967d91c017d9da827bab183cd6`
- Split: fixed internal GEARS-compatible seen0/seen1/seen2/random_combo split
- Status: not official GEARS and not leaderboard-comparable

## Method

The packaged baseline is `weighted_pca_ridge_s075_a10`: a PCA/Ridge residual correction over a weighted combo additive baseline.

Primary command:

```powershell
python scripts/run_norman_residual_multiseed.py --config configs/experiment/gears_norman_v017_multiseed_residual.yaml
```

## Result

| metric | value |
| --- | ---: |
| MAE | 0.430778 |
| MSE | 3.668870 |
| Pearson delta | 0.869224 |
| Spearman logFC | 0.784976 |

Seeds: `0, 1, 2, 3, 4`

Reference output:

```text
outputs/runs/v0.17-norman-validated-residual-baseline/gears_norman_scperturb_v013/20260625T100322Z/
```

Critical leakage stress checks passed.

## Reproducibility

- No-data smoke path is available for GitHub reviewers.
- With-data reproduction requires local Norman H5AD placement and checksum validation.
- Model card, benchmark card, runbook, release notes, and artifact manifest are included.

## Claim Boundary

This is a strong internal GEARS-compatible Norman baseline package. It is not official GEARS, not leaderboard-comparable, not SOTA, and not biological discovery.

## What I Want Feedback On

- Whether the benchmark framing is sufficiently clear for external review.
- Whether the residual baseline is a credible stepping stone toward official GEARS reproduction.
- Which public benchmark or official split should be prioritized next.
- How to improve the project page for AI-biology or computational biology mentors.

## Links And Read Order

1. `README.md`
2. `docs/V18_RELEASE_MODEL_CARD.md`
3. `docs/V18_BENCHMARK_CARD.md`
4. `docs/V17_EXTERNAL_RESULT_CARD.md`
5. `docs/V22_PUBLIC_DEMO_GUIDE.md`
6. `docs/V23_PROJECT_PAGE_ASSETS.md`
