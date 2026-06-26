# v0.24 Final Presentation Summary

## Positioning

EvoPrior-AIVC is ready for public repository review as a reproducible perturbation-prediction benchmark package. The strongest evidence remains the validated v0.17 residual baseline on a public Norman/scPerturb H5AD under a documented internal GEARS-compatible split.

## Evidence Snapshot

- Dataset: `NormanWeissman2019_filtered.h5ad`
- md5: `c870e6967d91c017d9da827bab183cd6`
- Split: internal GEARS-compatible seen0/seen1/seen2/random_combo
- Primary model: `weighted_pca_ridge_s075_a10`
- Seeds: `0, 1, 2, 3, 4`
- Metrics: MAE 0.430778, MSE 3.668870, Pearson 0.869224, Spearman 0.784976

## What This Demonstrates

- End-to-end data provenance and checksum discipline.
- Public benchmark-compatible ingestion and schema mapping.
- Locked split and leakage-audit workflow.
- Strong transparent and residual baselines.
- Release smoke, artifact manifest, and public-review documentation.

## What It Does Not Demonstrate

- Official GEARS result.
- Leaderboard comparability.
- SOTA or near-SOTA.
- Biological discovery or clinical utility.
- General model superiority beyond the documented split.

## v0.24 Deliverable

v0.24 converts the repository from "has publication assets" to "has an owner-ready publish/release/website package." It records that direct push and Release creation are still pending because no remote is configured and GitHub CLI is unavailable in this environment.

## Verification

- Targeted tests: `7 passed, 2 warnings`.
- Targeted ruff: passed.
- Artifact manifest: `reports/v0.24_artifact_manifest.md`, status `pass`.
- Release smoke: `outputs/runs/v0.19-release-smoke/20260626T024213Z/`, status `pass`.
- Full regression: `164 passed, 4 warnings`.

## Next Milestone

v0.25 should execute the actual public push or prepare a final mentor email package after the owner supplies a remote and explicit publishing approval.
