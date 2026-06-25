# Codex Handoff

## Current State

- Current branch: `feat/gears-norman-baseline-v013`
- Rollback point: `v0.12-public-benchmark-baseline-run`
- Latest completed milestone before this branch: `v0.12-public-benchmark-baseline-run`
- v0.13 target tag: `v0.13-gears-norman-baseline`
- Working tree: dirty with v0.13 source/config/docs/tests; local raw data and outputs must not be committed

## v0.13 Benchmark Decision

- Selected benchmark: `gears_norman_scperturb_v013`
- Dataset: Norman/Weissman 2019 filtered Perturb-seq from scPerturb Zenodo record 13350497
- Status: public-data, GEARS-compatible internal split
- Not official GEARS split
- Not leaderboard comparable
- Reason selected: recognized combinatorial perturbation benchmark family; legal public H5AD; file is below 2 GB; checksum is locked; local run completed today

## Data Source

- Source: <https://zenodo.org/records/13350497>
- Version: scPerturb Zenodo record v1.4
- File: `NormanWeissman2019_filtered.h5ad`
- Expected local path: `data/raw/NormanWeissman2019_filtered.h5ad`
- md5: `c870e6967d91c017d9da827bab183cd6`
- File size: 698,680,199 bytes
- License: CC-BY-4.0 via Zenodo record
- Local checksum status: `ok`

## Completed Commands

```powershell
python -m pytest -p no:cacheprovider --basetemp .tmp_pytest_v13
python -m pytest -p no:cacheprovider --basetemp .tmp_pytest_v13 tests/test_gears_norman_adapter.py tests/test_gears_splits.py tests/test_combo_additive_baseline.py tests/test_gears_metrics.py tests/test_gears_norman_config.py
python scripts/prepare_gears_norman.py --config configs/data/gears_norman_v013.yaml --dry-run
python scripts/prepare_gears_norman.py --config configs/data/gears_norman_v013.yaml
python scripts/run_gears_norman_baseline.py --config configs/experiment/gears_norman_v013_baseline.yaml
python scripts/run_public_benchmark_baseline.py --config configs/experiment/public_benchmark_v012_baseline.yaml
python scripts/run_evoprior_additive.py --config configs/experiment/real_v09_kang_evoprior_additive.yaml
python -m ruff check scripts/prepare_gears_norman.py scripts/run_gears_norman_baseline.py src/evoprior_aivc/data/gears_norman_adapter.py src/evoprior_aivc/data/gears_splits.py src/evoprior_aivc/baselines/combo_additive.py src/evoprior_aivc/evaluation/gears_metrics.py src/evoprior_aivc/baselines/__init__.py tests/test_gears_norman_adapter.py tests/test_gears_splits.py tests/test_combo_additive_baseline.py tests/test_gears_metrics.py tests/test_gears_norman_config.py
```

Results:

- Full tests: `136 passed, 2 warnings`.
- Targeted v0.13 tests: `7 passed, 2 warnings`.
- v0.13 prepare dry-run: passed.
- v0.13 runner: passed, output `outputs/runs/v0.13-gears-norman-baseline/gears_norman_scperturb_v013/20260625T002742Z/`.
- v0.12 backward compatibility runner: passed, output `outputs/runs/v0.12-public-benchmark-baseline-run/scperturb_papalexi_2021_arrayed_rna_v012/20260625T003054Z/`.
- v0.9 backward compatibility runner: passed, output `outputs/runs/v0.9-integrated-evoprior-additive/kang_2018_pbmc_ifnb/20260625T003115Z/`.
- Targeted ruff: passed.

## Current v0.13 Output

- Run directory: `outputs/runs/v0.13-gears-norman-baseline/gears_norman_scperturb_v013/20260625T002742Z/`
- Data report directory: `outputs/data_reports/gears_norman_scperturb_v013/20260625T002742Z/`
- Split: internal GEARS-compatible seen0/seen1/seen2 combo split
- Leakage audit: passed, no leaked test combos
- Test groups: 33 combo and 31 single groups
- Test classes: seen0=2, seen1=13, seen2=18, single_unseen=31

## Main Metric Snapshot

- `control_mean`: test MAE 0.8739, MSE 13.4469.
- `mean_delta`: test MAE 0.5939, MSE 7.6769, Pearson 0.6450, Spearman 0.4920.
- `single_effect_additive_combo`: test MAE 0.5491, MSE 6.1062, Pearson 0.7538, Spearman 0.5583.
- Combo-only `single_effect_additive_combo`: MAE 0.5938, MSE 6.5080, Pearson 0.8218, Spearman 0.6388.

## Claim Boundary

Allowed: v0.13 executed a reproducible public-data, GEARS-compatible internal Norman baseline run with documented data, split, metrics, schema report, leakage audit, and evidence artifacts.

Forbidden: SOTA, official GEARS, leaderboard comparability, biological discovery, neural GEARS reproduction, general EvoPrior superiority, or real evolutionary/conservation-prior benefit.

## Files Not To Commit

- `data/raw/`
- `outputs/`
- `.tmp_pytest_v13/`
- `.pytest_cache/`
- `.ruff_cache/`
- `*.egg-info/`

## Commands Still Required

```powershell
git status --short
git add .gitignore README.md configs docs reports src scripts tests pyproject.toml
git commit -m "feat: run gears norman baseline"
git tag v0.13-gears-norman-baseline
```

## Git Permission Blocker

Codex can edit files in the workspace but cannot write to `.git` in this session. Final staging, commit, and tag must be run by the user in PowerShell after verification passes.

## Next Exact Command

```powershell
git status --short
```
