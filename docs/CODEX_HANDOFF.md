# Codex Handoff

## Current State

- Current branch: `feat/public-benchmark-baseline-v012`
- Rollback point: `v0.11-external-public-benchmark-ingestion`
- Latest completed milestone before this branch: `v0.11-external-public-benchmark-ingestion`
- v0.12 target tag: `v0.12-public-benchmark-baseline-run`
- Working tree: dirty with v0.12 source/config/docs/tests plus local generated outputs and `.tmp_pytest/`

## v0.12 Benchmark Decision

- Selected benchmark: `scperturb_papalexi_2021_arrayed_rna_v012`
- Dataset: Papalexi/Satija 2021 ECCITE-seq RNA from scPerturb Zenodo record 13350497
- Status: public-data, custom benchmark-compatible split
- Not official leaderboard aligned
- Reason selected: legal public H5AD was already local, checksum locked, file is below 2 GB, and existing adapters/baselines support it today
- Deferred: GEARS/Norman official-style benchmark because no official data/split files are locally registered in v0.11

## Completed Commands

```powershell
python -m pytest -p no:cacheprovider tests/test_public_benchmark_metrics.py tests/test_public_benchmark_v012_config.py
python scripts/prepare_public_benchmark.py --config configs/data/public_benchmark_v012.yaml --dry-run
python scripts/prepare_public_benchmark.py --config configs/data/public_benchmark_v012.yaml
python scripts/run_public_benchmark_baseline.py --config configs/experiment/public_benchmark_v012_baseline.yaml
python -m ruff check scripts/prepare_public_benchmark.py scripts/run_public_benchmark_baseline.py src/evoprior_aivc/evaluation/public_benchmark_metrics.py tests/test_public_benchmark_metrics.py tests/test_public_benchmark_v012_config.py
python scripts/run_lineage_real_benchmark.py --config configs/experiment/real_v06_multicell_lineage.yaml
python scripts/run_evoprior_additive.py --config configs/experiment/real_v09_kang_evoprior_additive.yaml
python -m pytest -p no:cacheprovider
```

## Current v0.12 Output

- Run directory: `outputs/runs/v0.12-public-benchmark-baseline-run/scperturb_papalexi_2021_arrayed_rna_v012/20260624T150442Z/`
- Data report directory: `outputs/data_reports/scperturb_papalexi_2021_arrayed_rna_v012/20260624T150442Z/`
- Data checksum: md5 `843820d48b024348d6132cd53be0da91`
- Checksum status: `ok`
- Split: custom leave-one-perturbation suite over guide-level pseudobulk groups
- Held-out perturbations: `etv7`, `pdl1`
- Leakage audit: passed
- Test metric caveat: underpowered, `n=2`

## Main Metric Snapshot

- `no_change` / `control_mean`: test MAE 0.2388, MSE 1.7221, DE top-20 precision 0.0000
- `mean_delta` / `perturbation_mean_delta_v2` / `hierarchical_additive` / `evoprior_additive_no_prior`: test MAE 0.6922, MSE 5.7392, Pearson 0.5692, Spearman 0.3210, DE top-20 precision 0.5125
- `ridge_cv`: test MAE 0.7152, MSE 6.0478, Pearson 0.5656, Spearman 0.3181, DE top-20 precision 0.5125

## Claim Boundary

Allowed: v0.12 executed a reproducible public-data, benchmark-compatible baseline run with documented data, split, metrics, schema report, leakage audit, and evidence artifacts.

Forbidden: SOTA, official benchmark, leaderboard comparability, biological discovery, neural EvoPrior, general EvoPrior superiority, or real evolutionary/conservation-prior benefit.

## Files Not To Commit

- `data/raw/`
- `outputs/`
- `.tmp_pytest/`
- `.pytest_cache/`
- `.ruff_cache/`
- `*.egg-info/`

## Commands Still Required

```powershell
git status --short
git add README.md configs docs src scripts tests pyproject.toml
git commit -m "feat: run public benchmark baseline"
git tag v0.12-public-benchmark-baseline-run
```

## Git Permission Blocker

Codex attempted:

```powershell
git add README.md configs docs src scripts tests pyproject.toml
```

Result:

```text
fatal: Unable to create 'C:/Users/HiC3C/Documents/AIVC/.git/index.lock': Permission denied
```

The code and regression work are complete, but staging, commit, and tag require a shell with write access to `.git`.

## Next Exact Command

```powershell
git status --short
```

## Final Regression Result

- Full tests: `129 passed, 2 warnings`
- v0.12 prepare dry-run: passed
- v0.12 baseline runner: passed
- Targeted ruff on v0.12 Python files: passed
- v0.6 backward compatibility runner: passed, output `outputs/runs/v0.6-real-multicell-lineage-benchmark/kang_2018_pbmc_ifnb/20260624T150540Z/`
- v0.9 backward compatibility runner: passed, output `outputs/runs/v0.9-integrated-evoprior-additive/kang_2018_pbmc_ifnb/20260624T150550Z/`
