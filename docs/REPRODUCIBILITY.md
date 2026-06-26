# Reproducibility Runbook

## Environment

```powershell
python -m pip install -e ".[dev]"
```

Use a repository-local pytest temp directory on Windows:

```powershell
python -m pytest -p no:cacheprovider --basetemp .tmp_pytest_clean
```

## No-Data Smoke Test

```powershell
python scripts/run_release_smoke.py --config configs/experiment/release_smoke_v019.yaml
python scripts/check_release_artifacts.py
```

The smoke path verifies repository plumbing and artifact references without requiring raw Norman data.

## Data Verification

```powershell
python scripts/prepare_gears_norman.py --config configs/data/gears_norman_v013.yaml --dry-run
```

Expected md5 for the local Norman file:

```text
c870e6967d91c017d9da827bab183cd6
```

## Residual Baseline Reproduction

```powershell
python scripts/run_norman_residual_multiseed.py --config configs/experiment/gears_norman_v017_multiseed_residual.yaml
```

Expected key metric range, under the fixed internal split:

- MAE near `0.430778`
- MSE near `3.668870`
- Pearson delta near `0.869224`
- Spearman logFC near `0.784976`

## Additional Compatibility Checks

```powershell
python scripts/run_gears_norman_baseline.py --config configs/experiment/gears_norman_v014_aligned_baseline.yaml
python scripts/run_norman_residual_sprint.py --config configs/experiment/gears_norman_v016_residual_sweep.yaml
python scripts/run_official_gears_wrapper.py --config configs/experiment/gears_norman_v014_official_wrapper.yaml --dry-run
```

The official GEARS wrapper is feasibility-only. It does not produce official GEARS training, official split evaluation, or leaderboard-comparable metrics.
