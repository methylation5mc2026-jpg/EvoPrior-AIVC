# Claims And Evidence

## Supported Claim

EvoPrior-AIVC contains a reproducible internal GEARS-compatible Norman benchmark package with a validated residual baseline on a public Norman/scPerturb H5AD under a fixed split and locked internal metrics.

## Evidence

| evidence item | location |
| --- | --- |
| Dataset source and checksum | `docs/DATA.md` |
| Benchmark definition | `docs/BENCHMARK_CARD.md` |
| Model definition | `docs/MODEL_CARD.md` |
| Reproduction commands | `docs/REPRODUCIBILITY.md` |
| Current result table | `README.md` |
| Limitations | `docs/KNOWN_LIMITATIONS.md` |
| Experiment summary | `docs/EXPERIMENT_LEDGER.md` |

## Metric Boundary

The reported MAE, MSE, Pearson delta, and Spearman logFC values are internal compatible metrics. They are not official GEARS leaderboard metrics.

## Forbidden Claims

- official GEARS result
- leaderboard-comparable result
- SOTA
- biological discovery
- clinical utility
- broad model superiority
- general evolutionary or conservation-prior benefit

## Current Public Result

| model | MAE | MSE | Pearson | Spearman |
| --- | ---: | ---: | ---: | ---: |
| residual baseline | 0.430778 | 3.668870 | 0.869224 | 0.784976 |

The result is valid only for the exact dataset, preprocessing, internal split, and metric implementation documented in this repository.
