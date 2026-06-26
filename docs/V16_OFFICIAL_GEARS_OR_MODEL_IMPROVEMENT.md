# v0.16 Official GEARS Or Model Improvement

## Official GEARS Status

Status: `import_ok_but_wrapper_metrics_not_implemented`

v0.16 successfully created an isolated `.venv_gears` environment and installed:

- `cell-gears==0.1.2`
- `torch==2.12.1+cpu`
- `torch-geometric==2.8.0`

Import check succeeded:

```powershell
.\.venv_gears\Scripts\python.exe -c "import torch; import torch_geometric; import gears; print('ok')"
```

Wrapper dry-run command:

```powershell
$env:PYTHONPATH='src'
$env:MPLCONFIGDIR='.tmp_mpl_gears'
.\.venv_gears\Scripts\python.exe scripts\run_official_gears_wrapper.py --config configs\experiment\gears_norman_v014_official_wrapper.yaml --dry-run
```

Dry-run output:

```text
outputs/runs/v0.14-official-gears-wrapper-blocked/gears_norman_scperturb_v013/20260625T025148Z/
outputs/runs/v0.16-official-gears-attempt/20260625T025148Z/blocker_report.md
```

## Remaining Official GEARS Blocker

The current project wrapper is a feasibility/blocker writer. It does not train or evaluate an official GEARS model and therefore cannot produce official GEARS Norman metrics.

## Project-Owned Improvement Result

Because official metrics were not available from the wrapper, v0.16 proceeded with the residual model-improvement sprint.

Selected model:

```text
weighted_pca_ridge_s075_a10
```

Output:

```text
outputs/runs/v0.16-model-improvement-sprint/gears_norman_scperturb_v013/20260625T031612Z/
```

Final test metrics:

- MAE: `0.4308`
- MSE: `3.6689`
- Pearson delta: `0.8692`
- Spearman logFC: `0.7850`

This improves over the v0.14 weighted baseline on MAE/MSE and over the v0.14 single-effect baseline on Pearson/Spearman under the same internal split.

## Claim Boundary

This is a GEARS-compatible internal residual sprint result. It is not an official GEARS result, not leaderboard-comparable, not SOTA, and not biological discovery.
