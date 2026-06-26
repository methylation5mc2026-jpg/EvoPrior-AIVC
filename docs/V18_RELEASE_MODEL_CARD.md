# v0.18 Release Model Card

## Model

- Name: EvoPrior-AIVC Norman Residual Baseline v0.17
- Family: residual correction over combo additive baseline, PCA + Ridge residual
- Primary configuration: `weighted_pca_ridge_s075_a10`
- Config: `configs/experiment/gears_norman_v017_multiseed_residual.yaml`
- Script: `scripts/run_norman_residual_multiseed.py`

## Intended Use

Perturbation-response prediction baseline on the project GEARS-compatible Norman combo perturbation split. This is intended for external review of reproducibility, leakage controls, ablations, and baseline strength.

## Not Intended Use

Clinical inference, biological discovery, official GEARS leaderboard claims, SOTA claims, or general model superiority claims.

## Training Data

- Dataset: `NormanWeissman2019_filtered.h5ad`
- Source: scPerturb Zenodo record 13350497, version 1.4
- Data checksum: `c870e6967d91c017d9da827bab183cd6`
- Local path: `data/raw/NormanWeissman2019_filtered.h5ad`

## Split

- Split: internal GEARS-compatible seen0/seen1/seen2/random_combo split
- Split seed: `1400`
- Split manifest: `outputs/runs/v0.17-norman-validated-residual-baseline/gears_norman_scperturb_v013/20260625T100322Z/split_manifest.csv`
- Official GEARS status: not official GEARS; official split and official metrics are not imported

## Reproduction

```powershell
python scripts/run_norman_residual_multiseed.py --config configs/experiment/gears_norman_v017_multiseed_residual.yaml
```

Output: `outputs/runs/v0.17-norman-validated-residual-baseline/gears_norman_scperturb_v013/20260625T100322Z/`

Seeds: `0, 1, 2, 3, 4`

## Metrics

Metrics file: `aggregate_metrics.csv`.

| metric | mean | std | 95% CI |
| --- | ---: | ---: | --- |
| MAE | 0.430778 | 0.000004 | [0.430775, 0.430782] |
| MSE | 3.668870 | 0.000006 | [3.668864, 3.668875] |
| Pearson delta | 0.869224 | 0.000000 | [0.869224, 0.869224] |
| Spearman logFC | 0.784976 | 0.000006 | [0.784971, 0.784982] |

## Baselines Compared

Comparison file: `comparison_to_v014_v015_v016.csv`.

| baseline | MAE | MSE | Pearson | Spearman |
| --- | ---: | ---: | ---: | ---: |
| v0.14 `weighted_combo_additive` | 0.5660 | 6.6759 | 0.7599 | 0.6390 |
| v0.15 fast MLP/PCA | 0.5877 | 7.5517 | 0.7134 | 0.6317 |
| v0.16 residual | 0.430775 | 3.668888 | 0.869223 | 0.784999 |
| v0.17 validated residual | 0.430778 | 3.668870 | 0.869224 | 0.784976 |

## Leakage And Ablation

- Leakage audit: all critical checks passed.
- Leakage file: `leakage_stress_checks.csv`
- Ablation table: `ablation_summary.csv`
- Validation-selected ablation winner: `pca_ridge_residual_only`
- Shuffled residual-target control degraded to MAE/MSE `0.598936 / 8.050228`.
- Shuffled perturbation-feature control degraded to MAE/MSE `0.584434 / 7.413003`.

## Limitations

The result is internal GEARS-compatible, not official GEARS. Repeat variability is near zero because the selected PCA/ridge path is nearly deterministic under the fixed split. This supports reproducibility, not broad external uncertainty.

## Claim Boundary

Allowed: On the fixed project GEARS-compatible Norman split, `weighted_pca_ridge_s075_a10` reproducibly matches v0.16 across five seeds and outperforms documented v0.14/v0.15 internal baselines.

Forbidden: official GEARS, leaderboard comparability, SOTA, biological discovery, or broad model superiority.
