# v0.14 GEARS Wrapper Runbook

## Purpose

This runbook documents how v0.14 probes official GEARS/cell-gears feasibility without making GEARS a required project dependency.

## Dry Run

```powershell
python scripts/run_official_gears_wrapper.py --config configs/experiment/gears_norman_v014_official_wrapper.yaml --dry-run
```

Expected current result:

- output under `outputs/runs/v0.14-official-gears-wrapper-blocked/gears_norman_scperturb_v013/<timestamp>/`;
- `wrapper_feasibility.json`;
- `blocker_report.md`;
- decision `document_blocker`.

## Full Wrapper Attempt

```powershell
python scripts/run_official_gears_wrapper.py --config configs/experiment/gears_norman_v014_official_wrapper.yaml
```

This command remains blocker-first unless `gears`, `cell-gears`, `torch`, and the required GEARS runtime are importable.

## Current Environment Blocker

- `cell-gears`: not installed.
- `gears`: not importable.
- `torch`: not importable.
- `torch_geometric`: not importable.
- `pip install cell-gears`: blocked by `WinError 5` writing the Python user site.

## v0.16 Isolated Environment Update

v0.16 created an ignored `.venv_gears` environment and installed `cell-gears==0.1.2`, `torch==2.12.1+cpu`, and `torch-geometric==2.8.0`.

Import check status:

- `torch`: importable as `2.12.1+cpu`.
- `torch_geometric`: importable.
- `gears`: importable.

Wrapper status: the repository wrapper remains feasibility-only. It does not train or evaluate official GEARS and does not produce official GEARS Norman metrics. The v0.16 blocker is therefore implementation alignment, not dependency import.

## Claim Boundary

Wrapper dry-run/blocker artifacts are not model results. They only document why official GEARS execution is not available in the current environment.
