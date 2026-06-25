# v0.18 Benchmark Card

## Benchmark

- Name: Norman/scPerturb GEARS-compatible internal split
- Benchmark ID: `gears_norman_scperturb_v013`
- Dataset: `NormanWeissman2019_filtered.h5ad`
- Source: scPerturb Zenodo record 13350497, version 1.4
- Checksum: `c870e6967d91c017d9da827bab183cd6`

## Relation To GEARS

This benchmark is GEARS-compatible/internal. It uses Norman combinatorial perturbation data and seen0/seen1/seen2-style categories, but it does not import exact official GEARS split files or official metric scripts.

It is not an official GEARS leaderboard benchmark.

## Perturbations

- Perturbation types: single and combo perturbations
- Split categories: `seen0`, `seen1`, `seen2`, `random_combo`, `single_unseen`
- Split seed: `1400`
- Split manifest: `outputs/runs/v0.17-norman-validated-residual-baseline/gears_norman_scperturb_v013/20260625T100322Z/split_manifest.csv`

## Leakage Policy

- Residual model fitting uses train data only.
- Model selection uses validation metrics only.
- Test metrics are reported once after the selection protocol is fixed.
- Test combo perturbations must not appear in train or validation as combo targets.
- Leakage stress file: `leakage_stress_checks.csv`

## Metrics

Internal compatible metrics:

- MAE
- MSE
- Pearson delta correlation
- Spearman logFC correlation
- DE20/DE50 recovery summaries
- per-class and per-perturbation breakdowns

## Comparable Results

Comparable within this project:

- v0.14 `weighted_combo_additive`
- v0.15 fast MLP/PCA
- v0.16 residual sprint
- v0.17 validated residual baseline

Not comparable:

- official GEARS leaderboard or paper metrics unless exact official split, preprocessing, and metrics are matched.

## Known Official-Alignment Blockers

- Main environment lacks official GEARS/Torch dependencies.
- `.venv_gears` can import the dependency stack, but the repository wrapper is feasibility-only.
- Official GEARS split files are not imported.
- Official GEARS training/evaluation is not implemented in this repository wrapper.
