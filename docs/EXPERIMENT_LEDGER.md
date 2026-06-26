# Experiment Ledger

This ledger is a stable public summary. Full operational history is archived under `docs/archive/internal/`.

## Current Public Evidence

| item | value |
| --- | --- |
| Dataset | `NormanWeissman2019_filtered.h5ad` |
| Source | scPerturb Zenodo record 13350497, version 1.4 |
| Expected md5 | `c870e6967d91c017d9da827bab183cd6` |
| Benchmark ID | `gears_norman_scperturb_v013` |
| Split | fixed internal GEARS-compatible Norman split |
| Primary config | `configs/experiment/gears_norman_v017_multiseed_residual.yaml` |
| Primary command | `python scripts/run_norman_residual_multiseed.py --config configs/experiment/gears_norman_v017_multiseed_residual.yaml` |
| Reference output | `outputs/runs/v0.17-norman-validated-residual-baseline/gears_norman_scperturb_v013/20260625T100322Z/` |

## Baseline Progression

| model | MAE | MSE | Pearson | Spearman | note |
| --- | ---: | ---: | ---: | ---: | --- |
| `weighted_combo_additive` | 0.5660 | 6.6759 | 0.7599 | 0.6390 | transparent additive baseline |
| fast MLP/PCA | 0.5877 | 7.5517 | 0.7134 | 0.6317 | lightweight trained baseline |
| residual baseline | 0.430778 | 3.668870 | 0.869224 | 0.784976 | five-seed validated internal result |

## Validation Notes

- Leakage stress checks were run for the validated residual baseline.
- Model selection was validation-driven before final test reporting.
- Metrics are internal compatible metrics.
- Official GEARS execution remains blocked or feasibility-only in this repository.

## Claim Boundary

This ledger supports a narrow reproducible benchmark-engineering claim. It does not support official GEARS, leaderboard, SOTA, biological-discovery, clinical-use, or broad-superiority claims.
