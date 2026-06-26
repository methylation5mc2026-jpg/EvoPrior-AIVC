# v0.22 Public Demo Guide

## Five-Minute Review Path

1. Read `README.md`.
2. Read `docs/V18_RELEASE_MODEL_CARD.md`.
3. Read `docs/V18_BENCHMARK_CARD.md`.
4. Read `docs/V17_EXTERNAL_RESULT_CARD.md`.
5. Read `docs/V22_GITHUB_RELEASE_NOTES_FINAL.md`.

## Ten-Minute No-Data Smoke

```powershell
python -m pip install -e ".[dev]"
python -m pytest -p no:cacheprovider --basetemp .tmp_pytest_local tests/test_release_smoke_config.py tests/test_release_artifact_manifest.py tests/test_official_gears_diagnostics.py tests/test_ci_workflow_static.py
python scripts/check_ci_workflow.py --workflow .github/workflows/ci.yml
python scripts/run_release_smoke.py --config configs/experiment/release_smoke_v019.yaml
```

This path checks the release package without requiring raw Norman data.

## With-Data Reproduction

1. Obtain the public Norman/scPerturb H5AD described in `configs/data/gears_norman_v013.yaml`.
2. Place it at `data/raw/NormanWeissman2019_filtered.h5ad`.
3. Verify md5 `c870e6967d91c017d9da827bab183cd6`.
4. Run:

```powershell
python scripts/prepare_gears_norman.py --config configs/data/gears_norman_v013.yaml --dry-run
python scripts/run_norman_residual_multiseed.py --config configs/experiment/gears_norman_v017_multiseed_residual.yaml
python scripts/check_release_artifacts.py
```

## Expected Results

The reference v0.17 aggregate metrics are:

- MAE near `0.430778`
- MSE near `3.668870`
- Pearson delta near `0.869224`
- Spearman logFC near `0.784976`

Small numeric drift can occur if dependencies or preprocessing change. A meaningful public claim should always cite the exact command, output directory, commit, tag, data checksum, and split status.

## Troubleshooting

- Missing data: run `python scripts/prepare_gears_norman.py --config configs/data/gears_norman_v013.yaml --dry-run` and follow the printed placement/checksum instructions.
- Official GEARS blocked: current status is `import_ok_run_blocked`; this repository does not claim official GEARS metrics.
- Windows pytest temp permission: use `python -m pytest -p no:cacheprovider --basetemp .tmp_pytest_local`.
- Docker unavailable: v0.21 recorded Docker status `unavailable_docker`; Docker build/import is not part of the validated claim.
- Git permission issue in managed sandboxes: run `git add`, `git commit`, and `git tag` manually in a normal PowerShell session.
