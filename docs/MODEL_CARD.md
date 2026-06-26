# Model Card

## Model

Primary documented model: residual correction baseline for Norman/scPerturb combinatorial perturbation prediction.

Implementation entry point:

```text
src/evoprior_aivc/baselines/residual_combo_model.py
```

Reproduction script:

```powershell
python scripts/run_norman_residual_multiseed.py --config configs/experiment/gears_norman_v017_multiseed_residual.yaml
```

## Intended Use

This model is intended for reproducible benchmark engineering under a fixed internal GEARS-compatible Norman split. It is useful for checking data plumbing, split discipline, leakage audits, transparent baseline comparisons, and metric reporting.

## Not Intended For

- official GEARS leaderboard submission
- clinical or diagnostic use
- biological discovery claims
- broad claims of model superiority
- claims about evolutionary or conservation-prior benefit

## Data

- Dataset: `NormanWeissman2019_filtered.h5ad`
- Source: scPerturb Zenodo record 13350497, version 1.4
- Expected md5: `c870e6967d91c017d9da827bab183cd6`
- Local path: `data/raw/NormanWeissman2019_filtered.h5ad`

Raw data is not committed.

## Split And Evaluation

The model is evaluated on a fixed internal GEARS-compatible split with seen0/seen1/seen2/random_combo-style categories. The exact official GEARS split files and official metric scripts are not imported.

Metrics are internal compatible metrics:

- MAE
- MSE
- Pearson delta correlation
- Spearman logFC correlation
- DE recovery summaries
- per-class and per-perturbation breakdowns

## Primary Result

Five-seed validated internal result:

| metric | value |
| --- | ---: |
| MAE | 0.430778 |
| MSE | 3.668870 |
| Pearson delta | 0.869224 |
| Spearman logFC | 0.784976 |

## Safety And Claim Boundary

The model card supports a narrow engineering claim only: a validated residual baseline under a documented internal GEARS-compatible Norman setup. It is not an official GEARS result, not leaderboard-comparable, not SOTA, not biological discovery, and not clinical evidence.
