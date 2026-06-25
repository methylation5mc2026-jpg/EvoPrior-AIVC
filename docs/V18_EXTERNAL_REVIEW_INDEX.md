# v0.18 External Review Index

## Read First

1. `docs/V18_RELEASE_MODEL_CARD.md`
2. `docs/V18_BENCHMARK_CARD.md`
3. `docs/V18_REPRODUCIBILITY_RUNBOOK.md`
4. `docs/V17_EXTERNAL_RESULT_CARD.md`

## Result Summary

EvoPrior-AIVC has a validated residual baseline package on the public Norman/scPerturb GEARS-compatible internal split. The v0.17 residual model reproduces the v0.16 strong result across five seeds and remains stronger than the documented v0.14/v0.15 internal baselines, with ablations, negative controls, leakage stress checks, and exact reproduction commands.

## Benchmark Status

GEARS-compatible/internal. Not official GEARS, not leaderboard-comparable, and not SOTA.

## Best Result Table

| model | MAE | MSE | Pearson | Spearman |
| --- | ---: | ---: | ---: | ---: |
| v0.14 `weighted_combo_additive` | 0.5660 | 6.6759 | 0.7599 | 0.6390 |
| v0.15 fast MLP/PCA | 0.5877 | 7.5517 | 0.7134 | 0.6317 |
| v0.17 validated residual | 0.430778 | 3.668870 | 0.869224 | 0.784976 |

## Why v0.17 Is Credible

- Fixed split and checksum-locked public data.
- Five documented seeds: `0, 1, 2, 3, 4`.
- Validation-only selection policy.
- Negative controls degrade.
- Leakage stress checks pass.
- Reproducible command and artifact map.

## Not Claimed

No official GEARS result, no leaderboard comparability, no SOTA, no biological discovery, and no broad model superiority.

## Next Step To Official GEARS

Implement an actual official GEARS train/evaluate wrapper, import exact official split files, and match official metric scripts.

## File Map

- Model card: `docs/V18_RELEASE_MODEL_CARD.md`
- Benchmark card: `docs/V18_BENCHMARK_CARD.md`
- Runbook: `docs/V18_REPRODUCIBILITY_RUNBOOK.md`
- Official GEARS log: `docs/V18_OFFICIAL_GEARS_REPRODUCTION_LOG.md`
- External result card: `docs/V17_EXTERNAL_RESULT_CARD.md`
- Release manifest: `reports/v0.18_release_manifest.md`
- Output directory: `outputs/runs/v0.17-norman-validated-residual-baseline/gears_norman_scperturb_v013/20260625T100322Z/`
