# Benchmark Card

## Benchmark

- Name: Norman/scPerturb internal GEARS-compatible benchmark
- Benchmark ID: `gears_norman_scperturb_v013`
- Dataset: `NormanWeissman2019_filtered.h5ad`
- Source: scPerturb Zenodo record 13350497, version 1.4
- Expected md5: `c870e6967d91c017d9da827bab183cd6`

## Alignment Status

This benchmark is GEARS-compatible and internal. It uses public Norman combinatorial perturbation data and GEARS-style generalization categories, but it does not import exact official GEARS split files or official GEARS metric scripts.

It must not be described as an official GEARS leaderboard result.

## Split

- Split family: internal GEARS-compatible
- Categories: `seen0`, `seen1`, `seen2`, `random_combo`, `single_unseen`
- Split seed: `1400`
- Reference split manifest: `outputs/runs/v0.17-norman-validated-residual-baseline/gears_norman_scperturb_v013/20260625T100322Z/split_manifest.csv`

## Leakage Policy

- Fit residual models on train data only.
- Select models using validation metrics only.
- Report test metrics after the selection protocol is fixed.
- Do not use test combo targets during training or validation.
- Run leakage stress checks before interpreting the result.

## Metrics

Internal compatible metrics:

- MAE
- MSE
- Pearson delta correlation
- Spearman logFC correlation
- DE20/DE50 recovery summaries
- per-class and per-perturbation breakdowns

## Comparable Internal Baselines

| model | MAE | MSE | Pearson | Spearman |
| --- | ---: | ---: | ---: | ---: |
| `weighted_combo_additive` | 0.5660 | 6.6759 | 0.7599 | 0.6390 |
| fast MLP/PCA | 0.5877 | 7.5517 | 0.7134 | 0.6317 |
| residual baseline | 0.430778 | 3.668870 | 0.869224 | 0.784976 |

These results are comparable only within this repository's fixed data, split, preprocessing, and metric definitions.
