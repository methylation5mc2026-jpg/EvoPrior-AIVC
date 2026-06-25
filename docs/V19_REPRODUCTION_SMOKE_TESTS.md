# v0.19 Reproduction Smoke Tests

## Command

```powershell
python scripts/run_release_smoke.py --config configs/experiment/release_smoke_v019.yaml
```

## What It Checks

- `evoprior_aivc` imports.
- Required v0.18/v0.19 docs exist.
- Required configs and scripts exist.
- Norman raw file is present and md5 matches when available.
- v0.17 output directory and key metric files exist when available.
- A tiny residual baseline fixture runs and returns finite predictions.
- A targeted pytest subset passes.

## Missing Data Policy

Raw Norman data may be absent in a fresh public clone. The smoke script reports this as a warning with manual preparation instructions, not a permanent failure.

## Full Reproduction

Use the heavier command when local data is ready:

```powershell
python scripts/run_norman_residual_multiseed.py --config configs/experiment/gears_norman_v017_multiseed_residual.yaml
```

Expected key metrics are documented in `docs/V18_RELEASE_MODEL_CARD.md`.

## Latest Local Result

- Command: `python scripts/run_release_smoke.py --config configs/experiment/release_smoke_v019.yaml`
- Output: `outputs/runs/v0.19-release-smoke/20260625T223712Z/`
- Status: `pass`
- Targeted pytest subset inside smoke: passed.

The smoke script found the local Norman raw file and matched md5 `c870e6967d91c017d9da827bab183cd6` in this workspace.
