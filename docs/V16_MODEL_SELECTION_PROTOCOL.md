# v0.16 Model Selection Protocol

## Rule

v0.16 uses train for fitting, validation for model selection, and test once for the selected model.

## Data And Split

- Dataset: `gears_norman_scperturb_v013`
- Raw file: `data/raw/NormanWeissman2019_filtered.h5ad`
- md5: `c870e6967d91c017d9da827bab183cd6`
- Split: v0.14 internal GEARS-compatible seen0/seen1/seen2/random_combo split
- Config: `configs/experiment/gears_norman_v016_residual_sweep.yaml`

## Selection Metric

- Validation split: `val`
- Primary metric: `mae_delta`
- Direction: minimize
- Tie-breakers: lower `mse_delta`, higher `pearson_delta`

## Candidate Family

All candidates use an additive combo baseline as the base prediction and train only a residual correction:

```text
predicted_delta = additive_base_delta + residual_scale * residual_model(features)
```

Candidate residual models:

- base-only control
- direct ridge residual
- PCA residual + ridge
- PCA residual + sklearn MLP

## Test Policy

The test split is evaluated after validation selects one candidate. Test metrics are not used to change the candidate grid, residual scale, alpha, PCA components, hidden size, or selected model.

## Selected v0.16 Candidate

- Candidate: `weighted_pca_ridge_s075_a10`
- Base: `weighted_combo_additive`
- Residual model: `pca_ridge`
- Residual scale: `0.75`
- Alpha: `10.0`
- PCA components: `16`
- Random state: `1603`

Output:

```text
outputs/runs/v0.16-model-improvement-sprint/gears_norman_scperturb_v013/20260625T031612Z/
```
