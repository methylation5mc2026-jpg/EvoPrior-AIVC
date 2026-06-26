# v0.23 GitHub Publish Guide

## Preconditions

Before publishing:

- Working tree is clean after committing v0.23.
- Tag `v0.22-public-github-finalization` exists.
- Raw data is not tracked.
- Generated run outputs and release bundles are not tracked.
- `python scripts/check_release_artifacts.py` passes.
- The README renders clearly in a local Markdown preview or GitHub preview.

## Suggested Repository Name

`EvoPrior-AIVC`

## Suggested Repository Description

Reproducible single-cell perturbation-response benchmark pipeline with structured priors and a validated Norman/GEARS-compatible residual baseline.

## Suggested Topics

- `single-cell`
- `perturb-seq`
- `computational-biology`
- `gene-perturbation`
- `benchmark`
- `reproducibility`
- `ai-for-biology`
- `scperturb`
- `norman`
- `gears-compatible`

## Add A Remote

Use the repository URL created in GitHub:

```powershell
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin feat/github-publish-assets-v023
git push origin --tags
```

Do not push from this automation run unless explicitly instructed.

## Default Branch Strategy

Option A: keep `feat/github-publish-assets-v023` as a review branch, then open a pull request into `main`.

Option B: create or update `main` locally, merge the release branch, then push `main`.

For a first public release, Option A is safer because it preserves a reviewable diff.

## What Not To Push

These should remain ignored or absent:

- `data/raw/`
- `outputs/runs/`
- `outputs/release/`
- `.venv/`
- `.venv_gears/`
- `.tmp_pytest*/`
- `.pytest_cache/`
- `.ruff_cache/`
- Docker build cache
- API keys or service credentials

## First GitHub Checks After Push

1. Confirm README renders.
2. Confirm GitHub Actions CI starts and completes.
3. Check links to model card, benchmark card, demo guide, release notes, and showcase index.
4. Create a release for tag `v0.23-github-publish-or-project-page-assets`.
5. Paste `docs/V23_GITHUB_RELEASE_BODY.md` into the release body.
6. Confirm no raw H5AD file or large generated output appears in the web UI.

## If CI Fails

1. Open the failed workflow log.
2. Confirm it is the no-data smoke path, not a missing raw-data failure.
3. Re-run locally:

```powershell
python -m pytest -p no:cacheprovider --basetemp .tmp_pytest_local tests/test_release_smoke_config.py tests/test_release_artifact_manifest.py tests/test_official_gears_diagnostics.py tests/test_ci_workflow_static.py
python scripts/run_release_smoke.py --config configs/experiment/release_smoke_v019.yaml
python scripts/check_release_artifacts.py
```

4. Fix only the failing release/CI issue. Do not change benchmark metrics or tune the model.

## Claim Boundary

Public description may say this repository contains a reproducible release package and validated internal GEARS-compatible Norman baseline.

Do not claim official GEARS, leaderboard comparability, SOTA, biological discovery, clinical use, or broad model superiority.
