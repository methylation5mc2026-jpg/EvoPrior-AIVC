# Technical Review Map

This document provides a technical reading path for reviewing EvoPrior-AIVC as a benchmark engineering repository.

## Recommended Order

1. `README.md` — project scope, main result, claim boundary, quickstart.
2. `docs/V18_RELEASE_MODEL_CARD.md` — model definition and evaluation details.
3. `docs/V18_BENCHMARK_CARD.md` — dataset, split, metrics, and benchmark scope.
4. `docs/V18_REPRODUCIBILITY_RUNBOOK.md` — reproduction procedure.
5. `docs/V17_EXTERNAL_RESULT_CARD.md` — result snapshot and audit summary.
6. `docs/V21_PUBLIC_DATA_ACQUISITION_GUIDE.md` — public data acquisition and checksum guidance.
7. `docs/KNOWN_FAILURES.md` — known blockers and limitations.

## Main Technical Claim

EvoPrior-AIVC packages a validated residual baseline on a public Norman/scPerturb dataset under a documented internal GEARS-compatible split.

## Boundary

The repository does not report official GEARS metrics, does not claim leaderboard comparability, and does not claim SOTA or biological discovery.

## Reproduction Paths

No-data smoke path:

```powershell
python -m pip install -e ".[dev]"
python -m pytest -p no:cacheprovider --basetemp .tmp_pytest_local
python scripts/run_release_smoke.py --config configs/experiment/release_smoke_v019.yaml
```

With local Norman data:

```powershell
python scripts/prepare_gears_norman.py --config configs/data/gears_norman_v013.yaml --dry-run
python scripts/run_norman_residual_multiseed.py --config configs/experiment/gears_norman_v017_multiseed_residual.yaml
python scripts/check_release_artifacts.py
```
