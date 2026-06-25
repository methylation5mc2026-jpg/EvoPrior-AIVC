# v0.19 Application Portfolio Summary

## Problem

Predict transcriptional response to genetic perturbations from public single-cell perturbation data.

## Benchmark

The current strongest package uses Norman/scPerturb combinatorial Perturb-seq data under a fixed GEARS-compatible internal split with seen0, seen1, seen2, random_combo, and single_unseen categories.

## Engineering

The repository implements data validation, checksum tracking, pseudobulk construction, split manifests, leakage audits, internal compatible metrics, DE recovery summaries, ablations, negative controls, and release manifests.

## Model

The validated baseline combines a weighted additive combo model with a PCA-Ridge residual correction. The v0.17 package evaluates seeds `0, 1, 2, 3, 4`.

## Result

The v0.17 residual baseline reports MAE `0.430778`, MSE `3.668870`, Pearson `0.869224`, and Spearman `0.784976`, improving over the v0.14 weighted additive baseline and v0.15 fast MLP/PCA baseline under the same internal split.

## Honesty

This is not official GEARS, not leaderboard-comparable, not SOTA, and not a biological discovery claim.

## Next

The next technical step is official GEARS environment reproduction through Docker/WSL or a pinned clean environment with exact official split and metric alignment.

## v0.19 Packaging Status

This round adds repository-facing review polish: README entry points, metadata files, release smoke tests, official GEARS diagnostics, and an artifact manifest. It does not change the v0.17 model result or create a new benchmark performance claim.
