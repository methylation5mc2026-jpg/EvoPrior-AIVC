# v0.19 Official GEARS Unblock Plan

## Current Status

Status: `import_ok_run_blocked`.

The main Python environment does not import `torch`, `torch_geometric`, or `gears`. The isolated `.venv_gears` environment imports `torch 2.12.1+cpu`, `torch_geometric`, and `gears`, and the project wrapper dry-run reaches `run_official_wrapper_now`.

## Remaining Blocker

The blocker is implementation alignment: `scripts/run_official_gears_wrapper.py` records feasibility but does not train or evaluate official GEARS, does not import official split files, and does not produce official GEARS metrics.

## Diagnostic Command

```powershell
python scripts/diagnose_official_gears.py
```

Output:

```text
outputs/runs/v0.19-official-gears-diagnostics/<timestamp>/diagnostic_report.md
```

Latest local output:

```text
outputs/runs/v0.19-official-gears-diagnostics/20260625T223710Z/
```

Latest local status: `import_ok_run_blocked`.

## Recommended Manual Path

1. Prefer Docker or WSL for a clean Linux-like PyTorch/PyG stack.
2. Pin `torch`, `torch-geometric`, and `cell-gears` versions together.
3. Import official GEARS Norman split files and preprocessing steps.
4. Implement an official train/evaluate wrapper separate from the feasibility probe.
5. Compare only after matching official split and metrics exactly.

## Claim Boundary

Until those steps are complete, the project must not claim official GEARS reproduction, leaderboard comparability, or SOTA.
