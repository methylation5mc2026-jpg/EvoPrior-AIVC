# Contributing

Thank you for reviewing or improving EvoPrior-AIVC.

## Scope

This repository prioritizes reproducible perturbation-response benchmarking, clear data provenance, leakage checks, and honest claim boundaries.

## Before Opening A Change

- Do not commit raw data, outputs, virtual environments, caches, or checkpoints.
- Keep benchmark split definitions fixed unless the change explicitly creates a new documented milestone.
- Do not tune on test metrics.
- Do not claim SOTA, official GEARS, or leaderboard comparability without exact official data, split, and metric alignment.

## Useful Checks

```powershell
python -m pytest -p no:cacheprovider --basetemp .tmp_pytest_local
python scripts/run_release_smoke.py --config configs/experiment/release_smoke_v019.yaml
python scripts/check_release_artifacts.py
```

## Documentation

Update `docs/CODEX_HANDOFF.md`, `docs/EXPERIMENT_LEDGER.md`, and `docs/CLAIMS_AND_EVIDENCE.md` when a milestone changes evidence or claim boundaries.
