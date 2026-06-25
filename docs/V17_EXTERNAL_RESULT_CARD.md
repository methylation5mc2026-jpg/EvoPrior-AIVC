# v0.17 External Result Card

## One-Liner

EvoPrior-AIVC now has a reproducible, five-seed residual baseline package on a public Norman/scPerturb GEARS-compatible internal split, with ablations, negative controls, confidence intervals, and leakage stress checks.

## Dataset

- Source: scPerturb Zenodo record 13350497, version 1.4
- File: `NormanWeissman2019_filtered.h5ad`
- md5: `c870e6967d91c017d9da827bab183cd6`
- Config: `configs/experiment/gears_norman_v017_multiseed_residual.yaml`
- Output: `outputs/runs/v0.17-norman-validated-residual-baseline/gears_norman_scperturb_v013/20260625T100322Z/`

## Split Status

GEARS-compatible/internal split with seen0, seen1, seen2, random_combo, and single_unseen classes. This is not the official GEARS leaderboard split.

## Baselines Compared

| model | MAE | MSE | Pearson | Spearman |
| --- | ---: | ---: | ---: | ---: |
| v0.14 `weighted_combo_additive` | 0.5660 | 6.6759 | 0.7599 | 0.6390 |
| v0.15 fast MLP/PCA | 0.5877 | 7.5517 | 0.7134 | 0.6317 |
| v0.16 residual | 0.430775 | 3.668888 | 0.869223 | 0.784999 |
| v0.17 residual five-seed mean | 0.430778 | 3.668870 | 0.869224 | 0.784976 |

## Multi-Seed Stability

Seeds: `0, 1, 2, 3, 4`.

The primary residual model is effectively deterministic under this setup; repeat-level standard deviations are near zero and the five-seed mean reproduces v0.16.

## Class Breakdown

| class | MAE | MSE | Pearson | Spearman |
| --- | ---: | ---: | ---: | ---: |
| random_combo | 0.479937 | 3.428181 | 0.882232 | 0.774598 |
| seen0 | 0.277298 | 1.320024 | 0.949748 | 0.873347 |
| seen1 | 0.452625 | 3.447901 | 0.906946 | 0.825928 |
| seen2 | 0.433591 | 4.690747 | 0.924467 | 0.870900 |

## Ablation Summary

Validation-selected ablation winner: `pca_ridge_residual_only`. It is a follow-up candidate; v0.17 does not revise the primary frozen model after inspecting test metrics.

Negative controls degraded:

- shuffled residual target: MAE 0.598936, MSE 8.050228;
- shuffled perturbation features: MAE 0.584434, MSE 7.413003.

## Leakage Stress Summary

All critical leakage stress checks passed. See `leakage_stress_report.md`.

## Reproduce

```powershell
python scripts/run_norman_residual_multiseed.py --config configs/experiment/gears_norman_v017_multiseed_residual.yaml
```

## What Can Be Claimed

On the fixed project GEARS-compatible Norman split, `weighted_pca_ridge_s075_a10` reproducibly matches the v0.16 residual result across five seeds and outperforms the documented v0.14/v0.15 internal baselines.

## What Cannot Be Claimed

No official GEARS result, no leaderboard comparability, no SOTA, no biological discovery, and no general model superiority.

## Next Step Toward Official GEARS

Replace the feasibility-only wrapper with an actual official GEARS train/evaluate path and import the exact official split and metric definitions.
