# Benchmarks

## Active Public Benchmark

| field | value |
| --- | --- |
| Benchmark ID | `gears_norman_scperturb_v013` |
| Dataset | `NormanWeissman2019_filtered.h5ad` |
| Source | scPerturb Zenodo record 13350497, version 1.4 |
| Expected md5 | `c870e6967d91c017d9da827bab183cd6` |
| Split | fixed internal GEARS-compatible Norman split |
| Metrics | internal compatible MAE, MSE, Pearson delta, Spearman logFC, DE recovery |
| Official GEARS status | not official; wrapper remains feasibility-only |

## Internal Baseline Comparison

| model | MAE | MSE | Pearson | Spearman | note |
| --- | ---: | ---: | ---: | ---: | --- |
| `weighted_combo_additive` | 0.5660 | 6.6759 | 0.7599 | 0.6390 | transparent combo additive baseline |
| fast MLP/PCA | 0.5877 | 7.5517 | 0.7134 | 0.6317 | lightweight sklearn baseline |
| residual baseline | 0.430778 | 3.668870 | 0.869224 | 0.784976 | five-seed validated internal result |

## Archived Benchmark Notes

Detailed historical benchmark notes are retained under `docs/archive/internal/` when needed for internal reconstruction. They are not required to understand the current public technical package.
