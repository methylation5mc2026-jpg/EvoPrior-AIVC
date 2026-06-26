# v0.14 External Review Package

## One-Liner

EvoPrior-AIVC is a reproducible perturbation-response prediction benchmark pipeline with lineage/gene-prior modules and GEARS-compatible Norman baselines.

## Benchmark

- Dataset: `NormanWeissman2019_filtered.h5ad`
- Source: scPerturb Zenodo record 13350497
- Checksum: md5 `c870e6967d91c017d9da827bab183cd6`
- Benchmark ID: `gears_norman_scperturb_v013`
- Split status: GEARS-compatible/internal, not official GEARS

## Outputs

```text
outputs/runs/v0.14-gears-aligned-baseline/gears_norman_scperturb_v013/20260625T014719Z/
outputs/runs/v0.14-official-gears-wrapper-blocked/gears_norman_scperturb_v013/20260625T014710Z/
```

## Reproduce

```powershell
python scripts/run_official_gears_wrapper.py --config configs/experiment/gears_norman_v014_official_wrapper.yaml --dry-run
python scripts/run_gears_norman_baseline.py --config configs/experiment/gears_norman_v014_aligned_baseline.yaml
```

## Baselines

- `no_change`
- `control_mean`
- `mean_delta`
- `perturbation_mean_delta_v2`
- `single_effect_additive_combo`
- `weighted_combo_additive`
- `ridge_cv`
- `evoprior_additive_no_prior`

## Main Test Metrics

| Baseline | MAE | MSE | Pearson | Spearman |
| --- | ---: | ---: | ---: | ---: |
| `mean_delta` | 0.6954 | 10.0818 | 0.5804 | 0.4322 |
| `single_effect_additive_combo` | 0.5745 | 6.7388 | 0.7684 | 0.6443 |
| `weighted_combo_additive` | 0.5660 | 6.6759 | 0.7599 | 0.6390 |

## Weighted Combo Per-Class Metrics

| Class | MAE | MSE | Pearson | Spearman |
| --- | ---: | ---: | ---: | ---: |
| `random_combo` | 0.7176 | 9.4414 | 0.6842 | 0.4603 |
| `seen0` | 0.5729 | 6.6539 | 0.7758 | 0.5143 |
| `seen1` | 0.5811 | 6.3659 | 0.8433 | 0.7873 |
| `seen2` | 0.5283 | 6.6451 | 0.8838 | 0.8069 |

## Official GEARS Blocker

The official wrapper is blocked in this environment:

- `cell-gears` not installed;
- `gears` not importable;
- `torch` not importable;
- `torch_geometric` not importable;
- `python -m pip install cell-gears` fails with `WinError 5` writing the Python user site.

## Claim Boundary

Allowed:

- v0.14 is a reproducible GEARS-compatible internal Norman package with official-wrapper blocker documentation.
- `weighted_combo_additive` has the best MAE/MSE among implemented transparent baselines under this exact split.

Forbidden:

- official GEARS result;
- leaderboard comparability;
- SOTA;
- neural GEARS reproduction;
- biological discovery;
- general EvoPrior superiority.

## Next Step

Create a clean writable environment with pinned GEARS/Torch/PyG dependencies, import official split files, and rerun the wrapper before any official or leaderboard-style claim.
