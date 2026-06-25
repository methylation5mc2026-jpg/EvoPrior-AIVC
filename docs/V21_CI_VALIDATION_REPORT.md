# v0.21 CI Validation Report

## Summary

Status: `static_validation_passed`.

The GitHub Actions workflow was validated locally by static checks. GitHub Actions itself was not executed in this environment.

## Workflow

Path: `.github/workflows/ci.yml`

## Static Validation Command

```powershell
python scripts/check_ci_workflow.py --workflow .github/workflows/ci.yml
```

Observed result: `pass`.

## What Was Checked

- Workflow file exists.
- YAML parses.
- Workflow references release-focused tests.
- Workflow references `scripts/run_release_smoke.py`.
- Workflow references `configs/experiment/release_smoke_v019.yaml`.
- Workflow does not reference raw data paths.
- Workflow does not run the heavy v0.17 multiseed benchmark.
- Workflow does not require Docker, official GEARS, or GPU.

## Local Test Command

```powershell
python -m pytest -p no:cacheprovider --basetemp .tmp_pytest_v21 tests/test_ci_workflow_static.py
```

Targeted v0.21 suite:

```powershell
python -m pytest -p no:cacheprovider --basetemp .tmp_pytest_v21 tests/test_ci_workflow_static.py tests/test_make_release_bundle.py tests/test_release_artifact_manifest.py tests/test_official_gears_diagnostics.py tests/test_release_smoke_config.py
```

Observed result: `11 passed, 2 warnings`.

Final full local regression:

```powershell
python -m pytest -p no:cacheprovider --basetemp .tmp_pytest_v21
```

Observed result: `164 passed, 4 warnings`.

## Claim Boundary

This is static CI validation only. It does not prove GitHub-hosted CI has run, and it is not benchmark evidence.
