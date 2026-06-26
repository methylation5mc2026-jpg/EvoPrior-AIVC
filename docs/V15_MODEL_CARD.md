# v0.15 Model Card: FastComboMLP-PCA

## Model

- Public name: `fast_combo_mlp_pca_sklearn`
- Code: `src/evoprior_aivc/baselines/fast_combo_mlp.py`
- Runner: `scripts/run_fast_neural_norman.py`
- Config: `configs/experiment/gears_norman_v015_fast_neural.yaml`

## Intended Use

Fast CPU baseline for Norman-style perturbation delta prediction under the repo's GEARS-compatible internal split.

## Non-Intended Use

- Official GEARS reproduction
- Leaderboard submission
- Biological discovery
- Evidence of general neural-model superiority
- Production biological decision support

## Inputs

The model uses only leakage-safe metadata features:

- perturbation genes parsed from `perturbation_genes`
- perturbation type
- cell type
- unknown-gene count/fraction for genes absent from the train vocabulary

The feature encoder is fitted on training metadata only.

## Target

The model predicts PCA coefficients of train delta expression, then reconstructs gene-level delta expression through inverse PCA.

## Backend

PyTorch is unavailable in the current environment. v0.15 therefore uses sklearn `MLPRegressor`; the report labels the backend as `sklearn_mlp_regressor_pca`.

## Training

- Seeds: 1510, 1511, 1512
- PCA components: 32
- Hidden layers: `[64]`
- Max iterations: 250
- Early stopping: enabled when enough train examples are available
- Test metrics were not used for tuning

## Evaluation Result

Output directory:

```text
outputs/runs/v0.15-fast-neural-norman-baseline/gears_norman_scperturb_v013/20260625T023033Z/
```

Across three seeds, the test metrics were:

- MAE: 0.5877 +/- 0.0470
- MSE: 7.5517 +/- 0.9729
- Pearson delta: 0.7134 +/- 0.0445
- Spearman logFC: 0.6317 +/- 0.0397

The v0.14 `weighted_combo_additive` reference remains stronger on test MAE/MSE under the same split.

## Risks

- Small model and compact feature set.
- Internal split, not official GEARS split.
- sklearn MLP convergence can vary by seed; seed summary is the primary result.
- Single-context Norman data does not support broad context or cell-type generalization claims.

