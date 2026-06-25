# v0.18 Official GEARS Reproduction Log

## Status

Status: `import_ok_run_blocked`.

v0.18 made one final controlled official GEARS/cell-gears attempt. The isolated `.venv_gears` environment can import the dependency stack, but the current repository wrapper is still feasibility-only and does not train or evaluate official GEARS.

## Main Environment Checks

```powershell
python -m pip show cell-gears
python -m pip show gears
python -m pip show torch
python -m pip show torch_geometric
python -c "import torch; print(torch.__version__)"
python -c "import gears; print('gears import ok')"
```

Result: `cell-gears`, `gears`, `torch`, and `torch_geometric` are not installed or importable in the main environment.

## Isolated Environment Checks

```powershell
$env:PYTHONPATH='src'
$env:MPLCONFIGDIR='.tmp_mpl_gears'
.\.venv_gears\Scripts\python.exe -c "import torch; print(torch.__version__); import torch_geometric; print('torch_geometric import ok'); import gears; print('gears import ok')"
```

Result:

- `torch`: `2.12.1+cpu`
- `torch_geometric`: import ok
- `gears`: import ok
- `cell-gears`: `0.1.2`

## Wrapper Attempts

Dry-run:

```powershell
$env:PYTHONPATH='src'
$env:MPLCONFIGDIR='.tmp_mpl_gears'
.\.venv_gears\Scripts\python.exe scripts/run_official_gears_wrapper.py --config configs/experiment/gears_norman_v014_official_wrapper.yaml --dry-run
```

Output: `outputs/runs/v0.14-official-gears-wrapper-blocked/gears_norman_scperturb_v013/20260625T102235Z/`

Decision: `run_official_wrapper_now`.

Full wrapper:

```powershell
$env:PYTHONPATH='src'
$env:MPLCONFIGDIR='.tmp_mpl_gears'
.\.venv_gears\Scripts\python.exe scripts/run_official_gears_wrapper.py --config configs/experiment/gears_norman_v014_official_wrapper.yaml
```

Output: `outputs/runs/v0.14-official-gears-wrapper/gears_norman_scperturb_v013/20260625T102255Z/`

Decision: `run_official_wrapper_now`.

## Blocker

The blocker has moved from dependency import to implementation alignment: the current wrapper records feasibility but does not implement official GEARS training/evaluation, does not import exact official GEARS split files, and does not emit official metrics.

## Claim Boundary

This log is an official-wrapper feasibility artifact. It is not an official GEARS result, not leaderboard-comparable, and not SOTA.
