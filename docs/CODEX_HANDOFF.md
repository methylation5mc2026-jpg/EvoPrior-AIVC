# Codex Handoff

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
- `python -m pip install cell-gears`: downloaded `cell_gears-0.1.2` and `torch-2.12.1`, then failed with `WinError 5` while writing `C:\Users\HiC3C\AppData\Roaming\Python`.

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
