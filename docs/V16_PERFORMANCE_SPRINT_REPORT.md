# v0.16 Performance Sprint Report

## One-Line Result

v0.16 selected `weighted_pca_ridge_s075_a10` by validation MAE and improved over the v0.14/v0.15 Norman internal baselines on final test MAE, MSE, Pearson delta, and Spearman logFC.

## Dataset

- Dataset: `gears_norman_scperturb_v013`
- Source: scPerturb Zenodo record 13350497, version 1.4
- File: `NormanWeissman2019_filtered.h5ad`
- md5: `c870e6967d91c017d9da827bab183cd6`
- Config: `configs/experiment/gears_norman_v016_residual_sweep.yaml`
- Command: `python scripts/run_norman_residual_sprint.py --config configs/experiment/gears_norman_v016_residual_sweep.yaml`

## Split

- Split: v0.14 internal GEARS-compatible seen0/seen1/seen2/random_combo split
- Official GEARS split: not imported
- Leakage audit: passed

## Output

```text
outputs/runs/v0.16-model-improvement-sprint/gears_norman_scperturb_v013/20260625T031612Z/
```

Key files:

- `validation_sweep.csv`
- `selected_config.yaml`
- `final_test_metrics.csv`
- `comparison_to_v014_v015.csv`
- `per_class_metric_summary.csv`
- `de_metric_summary.csv`
- `report.md`

## Final Test Metrics

| model | MAE | MSE | Pearson | Spearman |
| --- | ---: | ---: | ---: | ---: |
| v0.16 `weighted_pca_ridge_s075_a10` | 0.4308 | 3.6689 | 0.8692 | 0.7850 |
| v0.14 `weighted_combo_additive` | 0.5660 | 6.6759 | 0.7599 | 0.6390 |
| v0.14 `single_effect_additive_combo` | 0.5745 | 6.7388 | 0.7684 | 0.6443 |
| v0.15 `fast_combo_mlp_pca_sklearn` | 0.5877 | 7.5517 | 0.7134 | 0.6317 |

## Class Breakdown

| class | MAE | MSE | Pearson | Spearman |
| --- | ---: | ---: | ---: | ---: |
| random_combo | 0.4799 | 3.4282 | 0.8822 | 0.7746 |
| seen0 | 0.2773 | 1.3201 | 0.9497 | 0.8733 |
| seen1 | 0.4526 | 3.4479 | 0.9069 | 0.8259 |
| seen2 | 0.4336 | 4.6908 | 0.9245 | 0.8709 |
| single_unseen | 0.4268 | 3.7053 | 0.7082 | 0.6343 |

## DE Recovery

The selected model's combo-class DE20 precision ranges from `0.7438` on random_combo to `0.8154` on seen2. DE50 precision ranges from `0.8250` on random_combo to `0.8800` on seen2.

## Official GEARS Status

The isolated `.venv_gears` environment can import `gears`, `torch`, and `torch_geometric`, but the repo wrapper does not yet train/evaluate official GEARS. Official GEARS metrics remain unavailable.

## Claim Boundary

Allowed: v0.16 improved a project-owned residual baseline under a documented GEARS-compatible internal Norman split.

Forbidden: official GEARS, leaderboard comparability, SOTA, biological discovery, or broad model superiority.
