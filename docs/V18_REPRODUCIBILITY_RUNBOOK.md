# v0.18 Reproducibility Runbook

## Environment Check

Use a repository-local pytest temp directory on Windows if the default user temp directory is locked.

```powershell
python -m pytest -p no:cacheprovider --basetemp .tmp_pytest_v18
```

Expected current result: `153 passed, 4 warnings`.

## Verify Norman Data

```powershell
python scripts/prepare_gears_norman.py --config configs/data/gears_norman_v013.yaml --dry-run
```

Expected checksum: `c870e6967d91c017d9da827bab183cd6`.

## Run Validated Residual Baseline

```powershell
python scripts/run_norman_residual_multiseed.py --config configs/experiment/gears_norman_v017_multiseed_residual.yaml
```

Reference output:

```text
outputs/runs/v0.17-norman-validated-residual-baseline/gears_norman_scperturb_v013/20260625T100322Z/
```

Expected key metric range:

- MAE near `0.430778`
- MSE near `3.668870`
- Pearson near `0.869224`
- Spearman near `0.784976`

## Compatibility Checks

```powershell
python scripts/run_gears_norman_baseline.py --config configs/experiment/gears_norman_v014_aligned_baseline.yaml
python scripts/run_norman_residual_sprint.py --config configs/experiment/gears_norman_v016_residual_sweep.yaml
python scripts/run_official_gears_wrapper.py --config configs/experiment/gears_norman_v014_official_wrapper.yaml --dry-run
```

## Official GEARS Feasibility Check

```powershell
$env:PYTHONPATH='src'
$env:MPLCONFIGDIR='.tmp_mpl_gears'
.\.venv_gears\Scripts\python.exe scripts/run_official_gears_wrapper.py --config configs/experiment/gears_norman_v014_official_wrapper.yaml --dry-run
```

Expected v0.18 status: `import_ok_run_blocked`. The dependency stack imports in `.venv_gears`, but the wrapper does not train or evaluate official GEARS.

## Troubleshooting

- `.git` permission issues: Codex may be unable to create `.git/index.lock`; run the printed `git add`, `git commit`, and `git tag` commands manually in PowerShell.
- Raw data: do not commit `data/raw/NormanWeissman2019_filtered.h5ad`.
- Outputs: do not commit `outputs/`; reports only reference output paths.
- Official GEARS: do not treat wrapper feasibility artifacts as official GEARS metrics.
- Long-running outputs: v0.17 multi-seed and ablation runs can take several minutes.
