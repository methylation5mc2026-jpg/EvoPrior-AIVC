# v0.21 Public Data Acquisition Guide

## Required Data File

`NormanWeissman2019_filtered.h5ad`

## Expected Checksum

```text
c870e6967d91c017d9da827bab183cd6
```

## Source

The project uses the public scPerturb Zenodo source documented in `configs/data/gears_norman_v013.yaml` and `docs/DATASETS.md`.

## Expected Local Path

```text
data/raw/NormanWeissman2019_filtered.h5ad
```

## Verify Access Instructions

```powershell
python scripts/prepare_gears_norman.py --config configs/data/gears_norman_v013.yaml --dry-run
```

## Verify Checksum In PowerShell

```powershell
Get-FileHash data/raw/NormanWeissman2019_filtered.h5ad -Algorithm MD5
```

The `Hash` field should equal:

```text
c870e6967d91c017d9da827bab183cd6
```

## What Not To Commit

Do not commit:

- `data/raw/NormanWeissman2019_filtered.h5ad`
- any raw H5AD files
- generated `outputs/runs/`
- generated `outputs/data_reports/`
- generated `outputs/release/` bundles
- virtual environments or cache directories

## No-Data Review Path

```powershell
python -m pip install -e ".[dev]"
python -m pytest -p no:cacheprovider --basetemp .tmp_pytest_local tests/test_release_smoke_config.py tests/test_release_artifact_manifest.py tests/test_official_gears_diagnostics.py tests/test_ci_workflow_static.py
python scripts/check_ci_workflow.py --workflow .github/workflows/ci.yml
python scripts/run_release_smoke.py --config configs/experiment/release_smoke_v019.yaml
```

## With-Data Reproduction Path

```powershell
python scripts/prepare_gears_norman.py --config configs/data/gears_norman_v013.yaml --dry-run
python scripts/run_norman_residual_multiseed.py --config configs/experiment/gears_norman_v017_multiseed_residual.yaml
python scripts/check_release_artifacts.py
```

## Claim Boundary

The data guide supports reproducibility. It does not grant leaderboard comparability, official GEARS status, SOTA status, or biological discovery claims.
