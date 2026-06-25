# v0.15 Fast Neural Norman Baseline

## Status

Completed locally on 2026-06-25.

## Objective

Train the first lightweight neural-style baseline in this repo on the public Norman/scPerturb GEARS-compatible internal benchmark package.

## Dataset

- Dataset ID: `gears_norman_scperturb_v013`
- Source: scPerturb Zenodo record 13350497, version 1.4
- File: `NormanWeissman2019_filtered.h5ad`
- Local path: `data/raw/NormanWeissman2019_filtered.h5ad`
- md5: `c870e6967d91c017d9da827bab183cd6`
- License: CC-BY-4.0 via scPerturb Zenodo record

## Split And Metrics

- Split: v0.14 internal GEARS-compatible seen0/seen1/seen2/random_combo split
- Official GEARS split: not imported
- Metric script: `src/evoprior_aivc/evaluation/gears_metrics.py`
- Metrics: MAE, MSE, Pearson delta, Spearman logFC, DE20/DE50 recovery, per-class breakdown
- Leakage audit: passed, no leaked test combos

## Model

- Name: `fast_combo_mlp_pca_sklearn`
- Backend: sklearn `MLPRegressor`
- Target reduction: PCA on train delta expression
- Features: train-only perturbation gene vocabulary, perturbation type, cell type, unknown-gene indicators
- Seeds: 1510, 1511, 1512
- Config: `configs/experiment/gears_norman_v015_fast_neural.yaml`
- Command: `python scripts/run_fast_neural_norman.py --config configs/experiment/gears_norman_v015_fast_neural.yaml`

## Output

```text
outputs/runs/v0.15-fast-neural-norman-baseline/gears_norman_scperturb_v013/20260625T023033Z/
```

## Main Test Metrics

| baseline | run kind | n seeds | MAE | MSE | Pearson delta | Spearman logFC |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `fast_combo_mlp_pca_sklearn` | trained neural sklearn | 3 | 0.5877 +/- 0.0470 | 7.5517 +/- 0.9729 | 0.7134 +/- 0.0445 | 0.6317 +/- 0.0397 |
| `single_effect_additive_combo` | recomputed reference | 0 | 0.5745 | 6.7388 | 0.7684 | 0.6443 |
| `weighted_combo_additive` | recomputed reference | 0 | 0.5660 | 6.6759 | 0.7599 | 0.6390 |

## Interpretation

The fast neural-style baseline trains and evaluates reproducibly, with seed-repeat reporting and full artifacts. It does not outperform the strongest v0.14 transparent reference on test MAE/MSE under this exact split.

## Claim Boundary

Allowed: this repo executed a reproducible fast sklearn MLP/PCA baseline on the public Norman/scPerturb GEARS-compatible internal split with documented data, split, metrics, and seed repeats.

Forbidden: SOTA, official GEARS, leaderboard comparability, biological discovery, or general neural-model superiority.

