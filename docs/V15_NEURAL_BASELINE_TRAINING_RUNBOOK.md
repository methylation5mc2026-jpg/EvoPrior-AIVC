# v0.15 Neural Baseline Training Runbook

## Preconditions

- Branch: `feat/fast-neural-norman-baseline-v015`
- Rollback tag: `v0.14-official-gears-alignment`
- Raw Norman H5AD present at `data/raw/NormanWeissman2019_filtered.h5ad`
- Raw data and outputs must not be committed

## Commands

Run targeted tests:

```powershell
python -m pytest -p no:cacheprovider --basetemp .tmp_pytest_v15 tests/test_perturbation_features.py tests/test_fast_combo_mlp_baseline.py tests/test_gears_norman_config.py
```

Run the v0.15 benchmark:

```powershell
python scripts/run_fast_neural_norman.py --config configs/experiment/gears_norman_v015_fast_neural.yaml
```

Run full regression:

```powershell
python -m pytest -p no:cacheprovider --basetemp .tmp_pytest_v15
```

Run minimal v0.14 compatibility:

```powershell
python scripts/run_gears_norman_baseline.py --config configs/experiment/gears_norman_v014_aligned_baseline.yaml
```

Run targeted ruff on v0.15 Python files:

```powershell
ruff check scripts/run_fast_neural_norman.py src/evoprior_aivc/baselines/fast_combo_mlp.py src/evoprior_aivc/data/perturbation_features.py tests/test_fast_combo_mlp_baseline.py tests/test_perturbation_features.py tests/test_gears_norman_config.py
```

## Completed Run

```text
outputs/runs/v0.15-fast-neural-norman-baseline/gears_norman_scperturb_v013/20260625T023033Z/
```

## Commit And Tag

Only after tests pass and no raw/output/cache files are staged:

```powershell
git add README.md configs docs reports src scripts tests pyproject.toml
git commit -m "feat: add fast neural Norman baseline"
git tag v0.15-fast-neural-norman-baseline
```

