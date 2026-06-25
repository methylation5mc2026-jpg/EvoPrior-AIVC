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

## Claim Boundary

Wrapper dry-run/blocker artifacts are not model results. They only document why official GEARS execution is not available in the current environment.
