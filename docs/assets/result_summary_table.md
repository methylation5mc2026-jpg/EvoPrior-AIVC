# Result Summary Table

Dataset: Norman/scPerturb `NormanWeissman2019_filtered.h5ad`

Checksum: `c870e6967d91c017d9da827bab183cd6`

Split: fixed internal GEARS-compatible seen0/seen1/seen2/random_combo split; not official GEARS.

| model | seeds | MAE | MSE | Pearson delta | Spearman logFC | status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| v0.14 weighted combo additive | 1 | 0.5660 | 6.6759 | 0.7599 | 0.6390 | transparent additive baseline |
| v0.15 fast MLP/PCA | 3 | 0.5877 | 7.5517 | 0.7134 | 0.6317 | lightweight trained baseline |
| v0.17 validated residual baseline | 5 | 0.430778 | 3.668870 | 0.869224 | 0.784976 | primary packaged result |

Claim boundary: internal GEARS-compatible Norman result only; not official GEARS, not leaderboard-comparable, not SOTA.
