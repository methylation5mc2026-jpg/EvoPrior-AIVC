# v0.20 GitHub Actions CI

## Workflow

Path: `.github/workflows/ci.yml`

The workflow is a no-data smoke check for public GitHub review. It does not require the Norman raw H5AD, official GEARS, a GPU, local outputs, or the v0.17 multiseed benchmark.

## Commands

```powershell
python -m pytest -p no:cacheprovider --basetemp .tmp_pytest_ci tests/test_release_smoke_config.py tests/test_release_artifact_manifest.py tests/test_official_gears_diagnostics.py
python scripts/run_release_smoke.py --config configs/experiment/release_smoke_v019.yaml
```

## Expected Behavior

- Missing raw Norman data is reported by the smoke script as a non-critical warning.
- Missing local v0.17 outputs are reported as a non-critical warning.
- The workflow validates package import, release docs/configs/scripts, tiny residual baseline plumbing, and the release-focused test subset.

## Claim Boundary

Passing CI means the public repository can execute a lightweight no-data smoke path. It is not a benchmark run, official GEARS reproduction, leaderboard result, SOTA claim, or biological discovery.
