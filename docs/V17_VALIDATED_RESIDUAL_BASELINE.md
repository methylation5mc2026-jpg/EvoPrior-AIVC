# v0.17 Validated Residual Baseline

## Frozen Setup

- Dataset: `data/raw/NormanWeissman2019_filtered.h5ad`
- Dataset md5: `c870e6967d91c017d9da827bab183cd6`
- Benchmark ID: `gears_norman_scperturb_v013`
- Split: v0.14 internal GEARS-compatible seen0/seen1/seen2/random_combo split
- Split manifest: `outputs/runs/v0.17-norman-validated-residual-baseline/gears_norman_scperturb_v013/20260625T100322Z/split_manifest.csv`
- Config: `configs/experiment/gears_norman_v017_multiseed_residual.yaml`
- Command: `python scripts/run_norman_residual_multiseed.py --config configs/experiment/gears_norman_v017_multiseed_residual.yaml`
- Seeds: `0, 1, 2, 3, 4`
- Output: `outputs/runs/v0.17-norman-validated-residual-baseline/gears_norman_scperturb_v013/20260625T100322Z/`

## Primary Result

Primary model: `weighted_pca_ridge_s075_a10`.

Metrics file: `aggregate_metrics.csv`.

| metric | mean | std | 95% CI |
| --- | ---: | ---: | --- |
| MAE | 0.430778 | 0.000004 | [0.430775, 0.430782] |
| MSE | 3.668870 | 0.000006 | [3.668864, 3.668875] |
| Pearson delta | 0.869224 | 0.000000 | [0.869224, 0.869224] |
| Spearman logFC | 0.784976 | 0.000006 | [0.784971, 0.784982] |

## Comparisons

Comparison file: `comparison_to_v014_v015_v016.csv`.

| baseline | MAE | MSE | Pearson | Spearman |
| --- | ---: | ---: | ---: | ---: |
| v0.14 `weighted_combo_additive` | 0.5660 | 6.6759 | 0.7599 | 0.6390 |
| v0.15 fast MLP/PCA | 0.5877 | 7.5517 | 0.7134 | 0.6317 |
| v0.16 `weighted_pca_ridge_s075_a10` | 0.430775 | 3.668888 | 0.869223 | 0.784999 |
| v0.17 five-seed mean | 0.430778 | 3.668870 | 0.869224 | 0.784976 |

## Class Breakdown

Breakdown file: `per_class_metric_summary.csv`.

| split class | MAE mean | MSE mean | Pearson mean | Spearman mean |
| --- | ---: | ---: | ---: | ---: |
| random_combo | 0.479937 | 3.428181 | 0.882232 | 0.774598 |
| seen0 | 0.277298 | 1.320024 | 0.949748 | 0.873347 |
| seen1 | 0.452625 | 3.447901 | 0.906946 | 0.825928 |
| seen2 | 0.433591 | 4.690747 | 0.924467 | 0.870900 |
| single_unseen | 0.426851 | 3.705323 | 0.708207 | 0.634221 |

## Claim Boundary

Allowed: On the project's fixed GEARS-compatible Norman split, `weighted_pca_ridge_s075_a10` reproduced the v0.16 residual baseline across five documented seeds and remained stronger than the v0.14/v0.15 internal baselines.

Forbidden: official GEARS, leaderboard comparability, SOTA, general biological discovery, or comparison to the GEARS paper unless exact official split and metrics are imported.
