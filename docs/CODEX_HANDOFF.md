# Codex Handoff

## Current State: v0.22 Public GitHub Finalization

- Current branch: `feat/public-github-finalization-v022`
- Rollback point: `v0.21-github-release-candidate-and-gears-docker-test`
- Latest completed source tag before this branch: `v0.21-github-release-candidate-and-gears-docker-test`
- v0.22 target tag: `v0.22-public-github-finalization`
- Working tree: dirty with v0.22 public-readiness docs, README polish, release bundle config, artifact checker updates, and tests; local raw data, generated outputs, caches, virtualenvs, and Docker build cache must not be committed.

## v0.22 Implemented So Far

- README first-screen polish for public review.
- Public sanitization report: `docs/V22_REPO_SANITIZATION_REPORT.md`
- Final GitHub release notes: `docs/V22_GITHUB_RELEASE_NOTES_FINAL.md`
- Repository profile copy: `docs/V22_GITHUB_REPO_PROFILE.md`
- Public demo guide: `docs/V22_PUBLIC_DEMO_GUIDE.md`
- Public final checklist: `docs/V22_PUBLIC_GITHUB_FINAL_CHECK.md`
- v0.22 release bundle config: `configs/release/v022_release_bundle.yaml`
- v0.22 artifact checker updates in `scripts/check_release_artifacts.py`

## v0.22 Verification So Far

- Plain `python -m pytest` failed because Windows denied access to `%LOCALAPPDATA%\Temp\pytest-of-<user>`; this is a host temp-permission issue.
- Repo-local temp validation before v0.22 edits: `python -m pytest -p no:cacheprovider --basetemp .tmp_pytest_v22` -> `164 passed, 4 warnings`.
- Tracked-file audit: no raw H5AD, checkpoint, pickle, NumPy archive, parquet, generated run output, or generated release bundle is tracked.
- Sensitive scan: no credential material or private agent paths found; historical user-specific Windows paths were generalized in public docs/configs.
- Targeted v0.22 tests: `python -m pytest -p no:cacheprovider --basetemp .tmp_pytest_v22 tests/test_make_release_bundle.py tests/test_release_artifact_manifest.py tests/test_release_smoke_config.py tests/test_ci_workflow_static.py` -> `7 passed, 2 warnings`.
- Final full regression: `python -m pytest -p no:cacheprovider --basetemp .tmp_pytest_v22` -> `164 passed, 4 warnings`.
- Targeted ruff on v0.22 modified Python/test files: passed.
- Release bundle: `python scripts/make_release_bundle.py --config configs/release/v022_release_bundle.yaml` -> `outputs/release/v0.22/20260626T000119Z/`.
- Artifact manifest: `python scripts/check_release_artifacts.py` -> `reports/v0.22_artifact_manifest.json`, status `pass`.
- Release smoke: `python scripts/run_release_smoke.py --config configs/experiment/release_smoke_v019.yaml` -> `outputs/runs/v0.19-release-smoke/20260626T000135Z/`, status `pass`.

## v0.22 Claim Boundary

Allowed: public GitHub/mentor review finalization, sanitized README/docs, release notes, public demo guide, repo profile copy, no-data smoke path, and release bundle around the validated v0.17 Norman residual baseline.

Forbidden: official GEARS result, Docker validation success, leaderboard comparability, SOTA, biological discovery, clinical claim, new benchmark performance result, or broad model superiority.

## v0.22 Files Not To Commit

- `data/raw/`
- `outputs/runs/`
- `outputs/data_reports/`
- `outputs/release/*` except `outputs/release/.gitkeep`
- `.venv/`
- `.venv_gears/`
- `.tmp_pytest_v22/`
- `.pytest_cache/`
- `.ruff_cache/`
- Docker build cache

## v0.22 Next Exact Command

Codex attempted to stage v0.22 files, but `.git/index.lock` creation failed with `Permission denied`. Workspace files are ready; user-side commit/tag is required:

```powershell
git status --short
git add README.md configs docs reports scripts tests src pyproject.toml LICENSE CITATION.cff CONTRIBUTING.md SECURITY.md .env.example .github docker .gitignore
git commit -m "docs: finalize public GitHub review package"
git tag v0.22-public-github-finalization
git tag --points-at HEAD
git status --short
```

## Current State: v0.21 GitHub Release Candidate And GEARS Docker Test

- Current branch: `feat/release-candidate-gears-docker-v021`
- Rollback point: `v0.20-github-release-or-official-gears-docker-env`
- Latest completed source tag before this branch: `v0.20-github-release-or-official-gears-docker-env`
- v0.21 target tag: `v0.21-github-release-candidate-and-gears-docker-test`
- Working tree: dirty with v0.21 release-candidate docs, CI static validator, release bundle config, artifact manifest updates, and tests; local raw data, generated outputs, caches, virtualenvs, and Docker build cache must not be committed.

## v0.21 Implemented

- Static CI workflow validator: `scripts/check_ci_workflow.py`
- v0.21 bundle config: `configs/release/v021_release_bundle.yaml`
- v0.21 docs: `docs/V21_RELEASE_CANDIDATE_PLAN.md`, `docs/V21_DOCKER_GEARS_TEST_REPORT.md`, `docs/V21_PUBLIC_DATA_ACQUISITION_GUIDE.md`, `docs/V21_GITHUB_RELEASE_NOTES.md`, `docs/V21_CI_VALIDATION_REPORT.md`
- v0.21 reports: `reports/v0.21_release_notes.md`, `reports/v0.21_artifact_manifest.md`, `reports/v0.21_artifact_manifest.json`
- Tests: `tests/test_ci_workflow_static.py` plus updated release bundle and artifact manifest tests.

## v0.21 Verification

- Baseline regression with repo-local temp before v0.21 edits: `python -m pytest -p no:cacheprovider --basetemp .tmp_pytest_v21` -> `162 passed, 4 warnings`.
- Targeted tests: `python -m pytest -p no:cacheprovider --basetemp .tmp_pytest_v21 tests/test_ci_workflow_static.py tests/test_make_release_bundle.py tests/test_release_artifact_manifest.py tests/test_official_gears_diagnostics.py tests/test_release_smoke_config.py` -> `11 passed, 2 warnings`.
- Final full regression: `python -m pytest -p no:cacheprovider --basetemp .tmp_pytest_v21` -> `164 passed, 4 warnings`.
- Targeted ruff on v0.21 Python files: passed.
- Static CI validation: `python scripts/check_ci_workflow.py --workflow .github/workflows/ci.yml` -> status `pass`.
- Release bundle: `python scripts/make_release_bundle.py --config configs/release/v021_release_bundle.yaml` -> `outputs/release/v0.21/20260625T233703Z/`.
- Release smoke: `python scripts/run_release_smoke.py --config configs/experiment/release_smoke_v019.yaml` -> `outputs/runs/v0.19-release-smoke/20260625T233315Z/`, status `pass`.
- Official GEARS diagnostic: `python scripts/diagnose_official_gears.py` -> `outputs/runs/v0.20-official-gears-diagnostics/20260625T233312Z/`, status `import_ok_run_blocked`.
- Docker availability commands: `docker --version`; `docker info` -> Docker unavailable/not on PATH.
- Artifact manifest: `python scripts/check_release_artifacts.py` -> `reports/v0.21_artifact_manifest.json`, status `pass`.

## v0.21 Claim Boundary

Allowed: release-candidate package around the validated v0.17 Norman residual baseline, static CI validation, no-data smoke, public data acquisition guide, artifact manifest, and honest Docker availability report.

Forbidden: official GEARS result, Docker build success, leaderboard comparability, SOTA, biological discovery, new benchmark performance result, or broad model superiority.

## v0.21 Files Not To Commit

- `data/raw/`
- `outputs/runs/`
- `outputs/data_reports/`
- `outputs/release/*` except `outputs/release/.gitkeep`
- `.venv/`
- `.venv_gears/`
- `.tmp_pytest_v21/`
- `.pytest_cache/`
- `.ruff_cache/`
- Docker build cache

## v0.21 Next Exact Command

Codex attempted `git add` for the v0.21 release-candidate files, but `.git/index.lock` creation failed with `Permission denied`. Workspace files are ready; user-side commit/tag is required:

```powershell
git status --short
git add README.md .github docker configs/release docs reports/v0.21_release_notes.md reports/v0.21_artifact_manifest.json reports/v0.21_artifact_manifest.md scripts/check_release_artifacts.py scripts/check_ci_workflow.py scripts/make_release_bundle.py tests/test_ci_workflow_static.py tests/test_make_release_bundle.py tests/test_release_artifact_manifest.py
git commit -m "docs: prepare v0.21 release candidate"
git tag v0.21-github-release-candidate-and-gears-docker-test
git tag --points-at HEAD
git status --short
```

## Current State: v0.20 GitHub Release Or Official GEARS Docker Env

- Current branch: `feat/github-release-or-gears-docker-v020`
- Rollback point: `v0.19-public-repo-polish-and-official-gears-unblock`
- Latest completed source tag before this branch: `v0.19-public-repo-polish-and-official-gears-unblock`
- v0.20 target tag: `v0.20-github-release-or-official-gears-docker-env`
- Working tree: dirty with v0.20 release engineering files, Docker/WSL GEARS route, tests, docs, and reports; local raw data, generated outputs, caches, virtualenvs, and Docker build cache must not be committed

## v0.20 Objective

Make the project GitHub-release ready and create a robust official GEARS environment-unblock path without changing the v0.17 model, split, metrics, or claim boundary.

## v0.20 Implemented So Far

- CI smoke workflow: `.github/workflows/ci.yml`
- Release bundle generator: `scripts/make_release_bundle.py`
- Release bundle config: `configs/release/v020_release_bundle.yaml`
- Docker/WSL GEARS route: `docker/Dockerfile.gears`, `docker/README_GEARS_ENV.md`
- Updated official GEARS diagnostic: `scripts/diagnose_official_gears.py`
- Updated artifact checker: `scripts/check_release_artifacts.py`
- v0.20 docs: `docs/V20_GITHUB_RELEASE_PLAN.md`, `docs/V20_OFFICIAL_GEARS_DOCKER_ENV.md`, `docs/V20_RELEASE_CHECKLIST.md`, `docs/V20_GITHUB_ACTIONS_CI.md`, `docs/V20_PUBLIC_REVIEW_README_MAP.md`
- Tests: `tests/test_make_release_bundle.py`, plus updated release artifact and GEARS diagnostic tests

## v0.20 Verification

- Plain `python -m pytest` failed because Windows denied access to `%LOCALAPPDATA%\Temp\pytest-of-<user>`; repo-local temp validation passed.
- Final v0.20 regression with repo-local temp: `python -m pytest -p no:cacheprovider --basetemp .tmp_pytest_v20` -> `162 passed, 4 warnings`.
- Targeted v0.20 tests: `python -m pytest -p no:cacheprovider --basetemp .tmp_pytest_v20 tests/test_make_release_bundle.py tests/test_release_artifact_manifest.py tests/test_official_gears_diagnostics.py tests/test_release_smoke_config.py` -> `9 passed, 2 warnings`.
- Targeted ruff on v0.20 Python files: passed.
- Release smoke: `python scripts/run_release_smoke.py --config configs/experiment/release_smoke_v019.yaml` -> `outputs/runs/v0.19-release-smoke/20260625T230440Z/`, status `pass`.
- Release bundle: `python scripts/make_release_bundle.py --config configs/release/v020_release_bundle.yaml` -> `outputs/release/v0.20/20260625T230630Z/`.
- Official GEARS diagnostic: `python scripts/diagnose_official_gears.py` -> `outputs/runs/v0.20-official-gears-diagnostics/20260625T230451Z/`, status `import_ok_run_blocked`.
- Artifact manifest: `python scripts/check_release_artifacts.py` -> `reports/v0.20_artifact_manifest.json`, status `pass`.
- Optional heavy v0.17 multiseed rerun was not repeated in v0.20; this milestone relies on the validated v0.17/v0.18 evidence and v0.19/v0.20 smoke/release checks.

## v0.20 Claim Boundary

Allowed: GitHub/release readiness, no-data CI smoke, small review bundle, artifact integrity checking, and Docker/WSL route toward official GEARS environment reproduction.

Forbidden: official GEARS result, leaderboard comparability, SOTA, biological discovery, new benchmark performance result, or general model superiority.

## v0.20 Files Not To Commit

- `data/raw/`
- `outputs/runs/`
- `outputs/data_reports/`
- `outputs/release/*` except `outputs/release/.gitkeep`
- `.venv/`
- `.venv_gears/`
- `.tmp_pytest_v20/`
- `.tmp_mpl_gears/`
- `.pytest_cache/`
- `.ruff_cache/`
- Docker build cache

## v0.20 Next Exact Command

Codex attempted to stage v0.20 files, but `.git/index.lock` creation failed with permission denied. No files were staged by Codex.

User-side commit/tag commands:

```powershell
git status --short
git add README.md .github docker configs/release docs reports/v0.20_artifact_manifest.json reports/v0.20_artifact_manifest.md scripts/check_release_artifacts.py scripts/diagnose_official_gears.py scripts/make_release_bundle.py tests/test_official_gears_diagnostics.py tests/test_release_artifact_manifest.py tests/test_make_release_bundle.py .gitignore outputs/release/.gitkeep
git commit -m "docs: prepare GitHub release and GEARS environment"
git tag v0.20-github-release-or-official-gears-docker-env
git tag --points-at HEAD
git status --short
```

## Current State: v0.19 Public Repo Polish And Official GEARS Unblock

- Current branch: `feat/public-repo-polish-v019`
- Rollback point: `v0.18-official-gears-reproduction-or-model-card-release`
- Latest completed source tag before this branch: `v0.18-official-gears-reproduction-or-model-card-release`
- v0.19 target tag: `v0.19-public-repo-polish-and-official-gears-unblock`
- Working tree: dirty with v0.19 repo-polish files, smoke scripts, diagnostics, tests, and small reports; local raw data, outputs, caches, `.venv_gears/`, and `.tmp_*` directories must not be committed

## v0.19 Objective

Make the repository reviewer-ready without changing the v0.17 model claim: tighten the README first screen, add public repo metadata, add release smoke checks, add artifact integrity checks, and record an official GEARS unblock diagnostic.

## v0.19 Implemented So Far

- Public repo metadata: `LICENSE`, `CITATION.cff`, `CONTRIBUTING.md`, `SECURITY.md`, `.env.example`.
- Release smoke config/script: `configs/experiment/release_smoke_v019.yaml`, `scripts/run_release_smoke.py`.
- Official GEARS diagnostic: `scripts/diagnose_official_gears.py`.
- Release artifact checker: `scripts/check_release_artifacts.py`.
- v0.19 docs: `docs/V19_PUBLIC_REPO_REVIEW_CHECKLIST.md`, `docs/V19_OFFICIAL_GEARS_UNBLOCK_PLAN.md`, `docs/V19_REPRODUCTION_SMOKE_TESTS.md`, `docs/V19_APPLICATION_PORTFOLIO_SUMMARY.md`.
- v0.19 reports: `reports/v0.19_application_portfolio_summary.md`, `reports/v0.19_artifact_manifest.md`, `reports/v0.19_artifact_manifest.json`.

## v0.19 Verification So Far

- Baseline full tests before v0.19 branch work: `153 passed, 4 warnings`.
- Targeted v0.19 tests: `python -m pytest -p no:cacheprovider --basetemp .tmp_pytest_v19 tests/test_release_smoke_config.py tests/test_official_gears_diagnostics.py tests/test_release_artifact_manifest.py` -> `5 passed, 2 warnings`.
- Targeted ruff on v0.19 Python files: passed.
- Full v0.19 regression: `python -m pytest -p no:cacheprovider --basetemp .tmp_pytest_v19` -> `158 passed, 4 warnings`.
- Release smoke: `python scripts/run_release_smoke.py --config configs/experiment/release_smoke_v019.yaml` -> `outputs/runs/v0.19-release-smoke/20260625T223712Z/`, status `pass`.
- Official GEARS diagnostic: `python scripts/diagnose_official_gears.py` -> `outputs/runs/v0.19-official-gears-diagnostics/20260625T223710Z/`, status `import_ok_run_blocked`.
- Artifact manifest: `python scripts/check_release_artifacts.py` -> `reports/v0.19_artifact_manifest.json`, status `pass`.
- Small fix made during smoke: the tiny residual smoke fixture now uses explicit string gene columns to match `DeltaDataset.gene_names`.

## v0.19 Claim Boundary

Allowed: the repository is packaged for external review around the validated v0.17 Norman residual baseline, with smoke checks and artifact integrity checks.

Forbidden: official GEARS reproduction, leaderboard comparability, SOTA, biological discovery, broad model superiority, or any new performance claim beyond the documented v0.17 internal split.

## v0.19 Files Not To Commit

- `data/raw/`
- `outputs/`
- `.venv_gears/`
- `.tmp_pytest_v19/`
- `.tmp_pytest_v19_smoke/`
- `.pytest_cache/`
- `.ruff_cache/`
- `*.egg-info/`

## v0.19 Next Exact Command

Codex attempted to stage v0.19 files, but `.git/index.lock` creation failed with permission denied. No files were staged by Codex.

User-side commit/tag commands:

```powershell
git status --short
git add README.md LICENSE CITATION.cff CONTRIBUTING.md SECURITY.md .env.example configs/experiment/release_smoke_v019.yaml docs reports/v0.19_application_portfolio_summary.md reports/v0.19_artifact_manifest.json reports/v0.19_artifact_manifest.md scripts/check_release_artifacts.py scripts/diagnose_official_gears.py scripts/run_release_smoke.py tests/test_official_gears_diagnostics.py tests/test_release_artifact_manifest.py tests/test_release_smoke_config.py
git commit -m "docs: polish public repo and GEARS unblock plan"
git tag v0.19-public-repo-polish-and-official-gears-unblock
git tag --points-at HEAD
git status --short
```

## Current State: v0.18 Official GEARS Reproduction Or Model-Card Release

- Current branch: `feat/gears-reproduction-or-release-v018`
- Rollback point: `v0.17-norman-validated-residual-baseline`
- Latest completed source tag before this branch: `v0.17-norman-validated-residual-baseline`
- v0.18 target tag: `v0.18-official-gears-reproduction-or-model-card-release`
- Working tree: dirty with v0.18 docs/reports only; local raw data, outputs, caches, `.venv_gears/`, `.tmp_mpl_gears/`, and `.tmp_pytest_v18/` must not be committed

## v0.18 Objective

Make one final controlled official GEARS feasibility attempt and package the validated v0.17 Norman residual baseline for external AI-biology review.

## v0.18 Official GEARS Status

- Status: `import_ok_run_blocked`
- Main environment: `cell-gears`, `gears`, `torch`, and `torch_geometric` are not installed/importable.
- Isolated environment: `.venv_gears` imports `torch 2.12.1+cpu`, `torch_geometric`, `gears`, and `cell-gears 0.1.2`.
- Dry-run output: `outputs/runs/v0.14-official-gears-wrapper-blocked/gears_norman_scperturb_v013/20260625T102235Z/`
- Full wrapper output: `outputs/runs/v0.14-official-gears-wrapper/gears_norman_scperturb_v013/20260625T102255Z/`
- v0.18 local status artifact: `outputs/runs/v0.18-official-gears-reproduction/20260625T102255Z/official_gears_status.md`
- Blocker: the repository wrapper is feasibility-only; it does not train/evaluate official GEARS, import official split files, or produce official metrics.

## v0.18 Release Package

- Model card: `docs/V18_RELEASE_MODEL_CARD.md`
- Benchmark card: `docs/V18_BENCHMARK_CARD.md`
- Reproducibility runbook: `docs/V18_REPRODUCIBILITY_RUNBOOK.md`
- Official GEARS log: `docs/V18_OFFICIAL_GEARS_REPRODUCTION_LOG.md`
- External review index: `docs/V18_EXTERNAL_REVIEW_INDEX.md`
- Release manifest: `reports/v0.18_release_manifest.md` and `reports/v0.18_release_manifest.json`
- External summary: `reports/v0.18_external_review_index.md`

## v0.18 Metrics Source

v0.18 does not change the model, split, or metrics. It packages the v0.17 output:

- Output: `outputs/runs/v0.17-norman-validated-residual-baseline/gears_norman_scperturb_v013/20260625T100322Z/`
- Dataset md5: `c870e6967d91c017d9da827bab183cd6`
- Seeds: `0, 1, 2, 3, 4`
- Primary model: `weighted_pca_ridge_s075_a10`
- Mean test MAE/MSE/Pearson/Spearman: 0.430778 / 3.668870 / 0.869224 / 0.784976.

## v0.18 Tests So Far

- Baseline full tests before branch creation: `153 passed, 4 warnings`.
- Full tests: `153 passed, 4 warnings`.
- Data dry-run: `python scripts/prepare_gears_norman.py --config configs/data/gears_norman_v013.yaml --dry-run` passed.
- v0.17 reproducibility runner: `outputs/runs/v0.17-norman-validated-residual-baseline/gears_norman_scperturb_v013/20260625T102713Z/`.
- v0.14 compatibility runner: `outputs/runs/v0.14-gears-aligned-baseline/gears_norman_scperturb_v013/20260625T103100Z/`.
- Official GEARS dry-run regression: `outputs/runs/v0.14-official-gears-wrapper-blocked/gears_norman_scperturb_v013/20260625T103300Z/`, decision `document_blocker`.
- Python ruff: not needed; v0.18 changed docs/reports only.

## v0.18 Claim Boundary

Allowed: v0.18 is an external review package for the validated v0.17 residual baseline and an official GEARS feasibility log.

Forbidden: official GEARS result, leaderboard comparability, SOTA, biological discovery, new performance result beyond v0.17, or broad model superiority.

## v0.18 Files Not To Commit

- `data/raw/`
- `outputs/`
- `.venv_gears/`
- `.tmp_mpl_gears/`
- `.tmp_pytest_v18/`
- `.pytest_cache/`
- `.ruff_cache/`
- `*.egg-info/`

## v0.18 Git Permission Blocker

Codex attempted to stage v0.18 files, but `.git/index.lock` creation failed with permission denied. No files are staged by Codex.

User-side commit/tag commands:

```powershell
git status --short
git add README.md docs reports configs scripts tests src pyproject.toml
git commit -m "docs: release validated Norman baseline package"
git tag v0.18-official-gears-reproduction-or-model-card-release
git tag --points-at HEAD
git status --short
```

## v0.18 Next Exact Command

```powershell
git add README.md docs reports configs scripts tests src pyproject.toml
```

## Current State: v0.17 Validated Norman Residual Baseline

- Current branch: `feat/norman-validated-residual-baseline-v017`
- Rollback point: `v0.16-official-gears-or-model-improvement-sprint`
- Latest completed source tag before this branch: `v0.16-official-gears-or-model-improvement-sprint`
- v0.17 target tag: `v0.17-norman-validated-residual-baseline`
- Working tree: dirty with v0.17 source/config/docs/tests; local raw data, outputs, caches, `.venv_gears/`, and `.tmp_*` directories must not be committed

## v0.17 Run Summary

- Config: `configs/experiment/gears_norman_v017_multiseed_residual.yaml`
- Command: `python scripts/run_norman_residual_multiseed.py --config configs/experiment/gears_norman_v017_multiseed_residual.yaml`
- Output: `outputs/runs/v0.17-norman-validated-residual-baseline/gears_norman_scperturb_v013/20260625T100322Z/`
- Dataset: `NormanWeissman2019_filtered.h5ad`, md5 `c870e6967d91c017d9da827bab183cd6`
- Split: fixed v0.14/v0.15/v0.16 internal GEARS-compatible seen0/seen1/seen2/random_combo split
- Seeds: `0, 1, 2, 3, 4`
- Primary model: `weighted_pca_ridge_s075_a10`

## v0.17 Metrics

- Five-seed test mean: MAE 0.430778, MSE 3.668870, Pearson 0.869224, Spearman 0.784976.
- v0.14 weighted reference: MAE 0.5660, MSE 6.6759, Pearson 0.7599, Spearman 0.6390.
- v0.15 fast MLP/PCA reference: MAE 0.5877, MSE 7.5517, Pearson 0.7134, Spearman 0.6317.
- v0.16 residual reference: MAE 0.430775, MSE 3.668888, Pearson 0.869223, Spearman 0.784999.
- Interpretation: v0.17 reproduces the v0.16 residual result across the documented seed list and packages it with validation artifacts.

## v0.17 Ablation And Leakage

- Ablation winner by validation MAE: `pca_ridge_residual_only`.
- Shuffled residual-target control degrades to MAE/MSE 0.598936 / 8.050228.
- Shuffled perturbation-feature control degrades to MAE/MSE 0.584434 / 7.413003.
- Leakage stress status: all critical checks pass.
- Official GEARS dry-run: `outputs/runs/v0.14-official-gears-wrapper-blocked/gears_norman_scperturb_v013/20260625T100234Z/`, decision `document_blocker`.

## v0.17 Final Regression

- v0.16 baseline full tests with repo-local temp: `148 passed, 4 warnings`.
- Targeted v0.17 tests: `12 passed, 3 warnings`.
- Targeted ruff on v0.17 Python files: passed.
- Full tests: `153 passed, 4 warnings`.
- v0.17 runner: `outputs/runs/v0.17-norman-validated-residual-baseline/gears_norman_scperturb_v013/20260625T100322Z/`.
- v0.16 compatibility runner: `outputs/runs/v0.16-model-improvement-sprint/gears_norman_scperturb_v013/20260625T101101Z/`.
- v0.14 compatibility runner: `outputs/runs/v0.14-gears-aligned-baseline/gears_norman_scperturb_v013/20260625T101302Z/`.
- Official GEARS dry-run recheck: `outputs/runs/v0.14-official-gears-wrapper-blocked/gears_norman_scperturb_v013/20260625T100234Z/`, decision `document_blocker`.
- Targeted ruff on v0.17 modified Python files: passed after regression.

## v0.17 Claim Boundary

Allowed: On the project's fixed GEARS-compatible Norman split, `weighted_pca_ridge_s075_a10` reproducibly matches the v0.16 residual result across five documented seeds and remains stronger than the v0.14/v0.15 internal baselines.

Forbidden: official GEARS, leaderboard comparability, SOTA, general biological discovery, comparison to the GEARS paper, or broad model superiority.

## v0.17 Files Not To Commit

- `data/raw/`
- `outputs/`
- `.venv_gears/`
- `.tmp_pytest_v17/`
- `.tmp_mpl_gears/`
- `.pytest_cache/`
- `.ruff_cache/`
- `*.egg-info/`

## v0.17 Git Permission Blocker

Codex attempted to stage v0.17 files, but `.git/index.lock` creation failed with permission denied. No files are staged by Codex.

User-side commit/tag commands:

```powershell
git status --short
git add README.md configs docs reports src scripts tests pyproject.toml
git commit -m "feat: validate Norman residual baseline"
git tag v0.17-norman-validated-residual-baseline
git tag --points-at HEAD
git status --short
```

## v0.17 Next Exact Command

```powershell
git add README.md configs docs reports src scripts tests pyproject.toml
```

## Current State: v0.16 Official GEARS Or Model Improvement Sprint

- Current branch: `feat/official-gears-or-model-improvement-v016`
- Rollback point: `v0.15-fast-neural-norman-baseline`
- Latest completed source tag before this branch: `v0.15-fast-neural-norman-baseline`
- v0.16 target tag: `v0.16-official-gears-or-model-improvement-sprint`
- Working tree: dirty with v0.16 source/config/docs/tests; local raw data, outputs, caches, `.venv_gears/`, and `.tmp_mpl_gears/` must not be committed

## v0.16 Objective

Try to unblock official GEARS locally. If official GEARS metrics remain unavailable, improve the project-owned Norman/scPerturb GEARS-compatible baseline without changing the locked internal split or tuning on test metrics.

## v0.16 Official GEARS Status

- Isolated environment: `.venv_gears/`
- Installed/importable: `cell-gears==0.1.2`, `torch==2.12.1+cpu`, `torch-geometric==2.8.0`, `gears`
- Dry-run command: `.\.venv_gears\Scripts\python.exe scripts\run_official_gears_wrapper.py --config configs\experiment\gears_norman_v014_official_wrapper.yaml --dry-run`
- Wrapper dry-run output: `outputs/runs/v0.14-official-gears-wrapper-blocked/gears_norman_scperturb_v013/20260625T025148Z/`
- v0.16 blocker artifact: `outputs/runs/v0.16-official-gears-attempt/20260625T025148Z/blocker_report.md`
- Status: imports are unblocked, but the repo wrapper is still feasibility-only and does not train/evaluate official GEARS or produce official GEARS metrics

## v0.16 Run Summary

- Config: `configs/experiment/gears_norman_v016_residual_sweep.yaml`
- Command: `python scripts/run_norman_residual_sprint.py --config configs/experiment/gears_norman_v016_residual_sweep.yaml`
- Output: `outputs/runs/v0.16-model-improvement-sprint/gears_norman_scperturb_v013/20260625T031612Z/`
- Dataset: `NormanWeissman2019_filtered.h5ad`, md5 `c870e6967d91c017d9da827bab183cd6`
- Split: v0.14/v0.15 internal GEARS-compatible seen0/seen1/seen2/random_combo split
- Selection: validation MAE only; final test metrics were not used to change the candidate grid
- Selected model: `weighted_pca_ridge_s075_a10`

## v0.16 Metrics

- Final test: MAE 0.4308, MSE 3.6689, Pearson 0.8692, Spearman 0.7850.
- v0.14 weighted reference: MAE 0.5660, MSE 6.6759, Pearson 0.7599, Spearman 0.6390.
- v0.15 fast MLP/PCA reference: MAE 0.5877, MSE 7.5517, Pearson 0.7134, Spearman 0.6317.
- Interpretation: v0.16 improves a project-owned residual baseline under one documented internal Norman split. It is not official GEARS, not SOTA, and not leaderboard-comparable.

## v0.16 Final Regression

- Start full tests: `144 passed, 3 warnings`.
- Targeted residual/config tests: `7 passed, 3 warnings`.
- Targeted ruff on v0.16 modified Python files: passed.
- Full tests: `148 passed, 4 warnings`.
- v0.16 runner: `outputs/runs/v0.16-model-improvement-sprint/gears_norman_scperturb_v013/20260625T031612Z/`.
- v0.14 compatibility runner: `outputs/runs/v0.14-gears-aligned-baseline/gears_norman_scperturb_v013/20260625T031201Z/`.
- v0.15 smoke runner: `outputs/runs/v0.15-fast-neural-norman-baseline-smoke/gears_norman_scperturb_v013/20260625T031407Z/`.

## v0.16 Files Not To Commit

- `data/raw/`
- `outputs/`
- `.venv_gears/`
- `.tmp_mpl_gears/`
- `.tmp_pytest_v16/`
- `.pytest_cache/`
- `.ruff_cache/`
- `*.egg-info/`

## v0.16 Git Permission Blocker

Codex attempted to stage v0.16 files, but `.git/index.lock` creation failed with permission denied. No files are staged by Codex.

User-side commit/tag commands:

```powershell
git status --short
git add .gitignore README.md configs/experiment/gears_norman_v016_residual_sweep.yaml docs reports/v0.16_norman_performance_sprint_summary.md scripts/run_fast_neural_norman.py scripts/run_norman_residual_sprint.py src/evoprior_aivc/baselines/__init__.py src/evoprior_aivc/baselines/residual_combo_model.py tests/test_gears_norman_config.py tests/test_residual_combo_model.py
git commit -m "feat: improve Norman baseline with residual sprint"
git tag v0.16-official-gears-or-model-improvement-sprint
git tag --points-at HEAD
git status --short
```

## v0.16 Next Exact Command

```powershell
git add .gitignore README.md configs/experiment/gears_norman_v016_residual_sweep.yaml docs reports/v0.16_norman_performance_sprint_summary.md scripts/run_fast_neural_norman.py scripts/run_norman_residual_sprint.py src/evoprior_aivc/baselines/__init__.py src/evoprior_aivc/baselines/residual_combo_model.py tests/test_gears_norman_config.py tests/test_residual_combo_model.py
```

## Current State: v0.15 Fast Neural Norman Baseline

- Current branch: `feat/fast-neural-norman-baseline-v015`
- Rollback point: `v0.14-official-gears-alignment`
- Latest completed source tag before this branch: `v0.14-official-gears-alignment`
- v0.15 target tag: `v0.15-fast-neural-norman-baseline`
- Working tree: dirty with v0.15 source/config/docs/tests; local raw data and outputs must not be committed

## v0.15 Run Summary

- Config: `configs/experiment/gears_norman_v015_fast_neural.yaml`
- Command: `python scripts/run_fast_neural_norman.py --config configs/experiment/gears_norman_v015_fast_neural.yaml`
- Output: `outputs/runs/v0.15-fast-neural-norman-baseline/gears_norman_scperturb_v013/20260625T023033Z/`
- Dataset: `NormanWeissman2019_filtered.h5ad`, md5 `c870e6967d91c017d9da827bab183cd6`
- Split: v0.14 internal GEARS-compatible seen0/seen1/seen2/random_combo split
- Leakage audit: passed, no leaked test combos
- Model: `fast_combo_mlp_pca_sklearn`, sklearn MLPRegressor over PCA-compressed train deltas
- Seeds: 1510, 1511, 1512

## v0.15 Metrics

- Fast neural test mean: MAE 0.5877, MSE 7.5517, Pearson 0.7134, Spearman 0.6317.
- Recomputed `single_effect_additive_combo`: MAE 0.5745, MSE 6.7388, Pearson 0.7684, Spearman 0.6443.
- Recomputed `weighted_combo_additive`: MAE 0.5660, MSE 6.6759, Pearson 0.7599, Spearman 0.6390.
- Interpretation: trained neural-style baseline is reproducible, but it does not beat the strongest v0.14 transparent baseline on test MAE/MSE.

## v0.15 Final Regression

- Targeted tests: `5 passed, 3 warnings`.
- Full tests: `144 passed, 3 warnings`.
- Targeted ruff on v0.15 Python files: passed.
- v0.15 runner: `outputs/runs/v0.15-fast-neural-norman-baseline/gears_norman_scperturb_v013/20260625T023033Z/`.
- v0.14 compatibility runner: `outputs/runs/v0.14-gears-aligned-baseline/gears_norman_scperturb_v013/20260625T023316Z/`.

## v0.15 Claim Boundary

Allowed: reproducible fast sklearn MLP/PCA baseline on a public Norman/scPerturb GEARS-compatible internal split with documented data, split, metrics, and seed repeats.

Forbidden: SOTA, official GEARS, leaderboard comparability, biological discovery, or general neural-model superiority.

## Files Not To Commit

- `data/raw/`
- `outputs/`
- `.tmp_pytest_v15/`
- `.pytest_cache/`
- `.ruff_cache/`
- `*.egg-info/`

## Git Permission Blocker

Codex attempted to stage v0.15 files, but `.git/index.lock` creation failed with permission denied. No files are staged.

User-side commit/tag commands:

```powershell
git add README.md configs/experiment/gears_norman_v015_fast_neural.yaml docs reports/v0.15_fast_neural_norman_summary.md scripts/run_fast_neural_norman.py src/evoprior_aivc/baselines/__init__.py src/evoprior_aivc/baselines/fast_combo_mlp.py src/evoprior_aivc/data/perturbation_features.py tests/test_fast_combo_mlp_baseline.py tests/test_perturbation_features.py tests/test_gears_norman_config.py
git commit -m "feat: add fast neural Norman baseline"
git tag v0.15-fast-neural-norman-baseline
git tag --points-at HEAD
git status --short
```

## Next Exact Command

```powershell
git add README.md configs/experiment/gears_norman_v015_fast_neural.yaml docs reports/v0.15_fast_neural_norman_summary.md scripts/run_fast_neural_norman.py src/evoprior_aivc/baselines/__init__.py src/evoprior_aivc/baselines/fast_combo_mlp.py src/evoprior_aivc/data/perturbation_features.py tests/test_fast_combo_mlp_baseline.py tests/test_perturbation_features.py tests/test_gears_norman_config.py
```

## Current State

- Current branch: `feat/official-gears-alignment-v014`
- Rollback point: `v0.13-gears-norman-baseline`
- Latest completed milestone before this branch: `v0.13-gears-norman-baseline`
- v0.14 target tag: `v0.14-official-gears-alignment`
- Working tree: dirty with v0.14 source/config/docs/tests; local raw data and outputs must not be committed

## v0.14 Objective

Move the Norman benchmark package from GEARS-compatible/internal toward official GEARS alignment. The official wrapper is attempted through optional dependency checks. If blocked, v0.14 must still produce a stronger GEARS-compatible aligned baseline package with explicit blocker documentation.

## Official GEARS Feasibility

- `python -m pip show cell-gears`: not installed.
- `python -m pip show gears`: not installed.
- `python -m pip show torch`: not installed.
- `python -m pip show torch_geometric`: not installed.
- `python -c "import gears"`: `ModuleNotFoundError`.
- `python -c "import torch"`: `ModuleNotFoundError`.
- `python -m pip install cell-gears`: downloaded `cell_gears-0.1.2` and `torch-2.12.1`, then failed with `WinError 5` while writing `%APPDATA%\Python`.

Decision: official GEARS wrapper is currently blocked by missing dependencies and user-site install permissions. v0.14 proceeds with an optional wrapper that writes a blocker report plus a tightened GEARS-compatible baseline.

## Implemented So Far

- Optional GEARS wrapper interface: `src/evoprior_aivc/external/gears_wrapper.py`
- Wrapper runner: `scripts/run_official_gears_wrapper.py`
- Wrapper config: `configs/experiment/gears_norman_v014_official_wrapper.yaml`
- v0.14 aligned baseline config: `configs/experiment/gears_norman_v014_aligned_baseline.yaml`
- Weighted combo baseline: `src/evoprior_aivc/baselines/combo_weighted.py`
- Split helper now supports `random_combo_fraction`.
- Combo additive fallback report now includes perturbation metadata.

## Targeted Tests

```powershell
python -m pytest -p no:cacheprovider --basetemp .tmp_pytest_v14 tests/test_gears_wrapper_interface.py tests/test_combo_weighted_baseline.py tests/test_gears_splits.py tests/test_gears_norman_config.py tests/test_combo_additive_baseline.py tests/test_gears_metrics.py tests/test_gears_norman_adapter.py
```

Result: `12 passed, 2 warnings`.

## Current v0.14 Outputs

- Official wrapper blocker: `outputs/runs/v0.14-official-gears-wrapper-blocked/gears_norman_scperturb_v013/20260625T014710Z/`
- Aligned baseline: `outputs/runs/v0.14-gears-aligned-baseline/gears_norman_scperturb_v013/20260625T014719Z/`
- Split status: GEARS-compatible/internal, not official GEARS.
- Leakage audit: passed, no leaked test combos.
- Test groups: 39 combo and 31 single groups.
- Test classes: random_combo=8, seen0=4, seen1=14, seen2=13, single_unseen=31.

## Main v0.14 Metric Snapshot

- `mean_delta`: test MAE 0.6954, MSE 10.0818, Pearson 0.5804, Spearman 0.4322.
- `single_effect_additive_combo`: test MAE 0.5745, MSE 6.7388, Pearson 0.7684, Spearman 0.6443.
- `weighted_combo_additive`: test MAE 0.5660, MSE 6.6759, Pearson 0.7599, Spearman 0.6390.

## Final Regression Result

- Full tests: `141 passed, 2 warnings`.
- Targeted v0.14 tests: `12 passed, 2 warnings`.
- v0.14 official wrapper dry-run: passed, output `outputs/runs/v0.14-official-gears-wrapper-blocked/gears_norman_scperturb_v013/20260625T014710Z/`.
- v0.14 aligned baseline runner: passed, output `outputs/runs/v0.14-gears-aligned-baseline/gears_norman_scperturb_v013/20260625T014719Z/`.
- v0.13 backward compatibility runner: passed, output `outputs/runs/v0.13-gears-norman-baseline/gears_norman_scperturb_v013/20260625T015053Z/`.
- v0.12 backward compatibility runner: passed, output `outputs/runs/v0.12-public-benchmark-baseline-run/scperturb_papalexi_2021_arrayed_rna_v012/20260625T015257Z/`.
- Targeted ruff on v0.14 modified Python files: passed.

## Files Not To Commit

- `data/raw/`
- `outputs/`
- `.tmp_pytest_v14/`
- `.pytest_cache/`
- `.ruff_cache/`
- `*.egg-info/`

## Next Exact Command

```powershell
git status --short
```
