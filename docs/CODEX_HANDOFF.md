# Codex handoff

## Current state

- Current branch: `feat/real-multicell-lineage-benchmark`
- Latest stable tag: `v0.6-real-multicell-lineage-benchmark`
- Latest commit: `b3cdf51 feat: add real multicell lineage benchmark`
- v0.7 tag: not present. `git tag --list "v0.*"` currently ends at `v0.6-real-multicell-lineage-benchmark`.

## Modified files summary

- Tracked, unstaged: 2 files
  - `src/evoprior_aivc/baselines/__init__.py`
  - `src/evoprior_aivc/priors/__init__.py`
- Untracked v0.7 paths: 22
  - `configs/experiment/real_v07_kang_gene_prior.yaml`
  - `configs/experiment/synthetic_v07_gene_prior.yaml`
  - `configs/priors/gene_prior_kang_v07.yaml`
  - `configs/priors/gene_prior_v07.yaml`
  - `docs/V07_GENE_EVOLUTIONARY_PRIOR_DESIGN.md`
  - `docs/V07_GENE_PRIOR_ABLATION_PLAN.md`
  - `docs/V07_GENE_PRIOR_SOURCES.md`
  - `scripts/prepare_gene_prior.py`
  - `scripts/run_gene_prior.py`
  - `src/evoprior_aivc/baselines/gene_prior_correction.py`
  - `src/evoprior_aivc/data/gene_prior_sources.py`
  - `src/evoprior_aivc/data/synthetic_gene_prior.py`
  - `src/evoprior_aivc/evaluation/prior_audit.py`
  - `src/evoprior_aivc/priors/gene_evolution.py`
  - `src/evoprior_aivc/priors/gene_features.py`
  - `src/evoprior_aivc/priors/gene_prior_table.py`
  - `tests/test_gene_evolution_prior.py`
  - `tests/test_gene_prior_correction_baseline.py`
  - `tests/test_gene_prior_sources.py`
  - `tests/test_gene_prior_table.py`
  - `tests/test_prior_audit.py`
  - `tests/test_synthetic_gene_prior.py`
- Staged changes: none. Both `git diff --cached --stat` and `git diff --cached --name-only` returned empty output.

## Staged and unstaged state

- Working tree is dirty.
- No files are staged.
- Dirty paths total: 24, consisting of 2 tracked modified files and 22 untracked files.

## Suspected interruption point

The v0.7 gene evolutionary/conservation prior work appears partially present as untracked files, with two package `__init__.py` files modified to expose the new modules. The current branch is still the v0.6 branch name, not the expected `feat/gene-evolutionary-prior-module`, so continuing should first confirm whether to keep this v0.7 work on the current branch or create/switch to the intended v0.7 branch while preserving all unstaged and untracked files.

Known prompt context says synthetic v0.7 showed strong bases such as `mean_delta` and `lineage_shrinkage` already captured much of the synthetic global gene modulation, and that a `gene_prior_correction_control_mean` weak-base sanity check may have been started. This must still be verified from repository files and targeted tests.

## Commands still required

- Inspect the v0.7 untracked files and the two modified `__init__.py` files.
- Run v0.7 targeted tests.
- If targeted tests fail, finish the interrupted weak-base sanity-check fix before running synthetic v0.7.
- Run synthetic v0.7.
- Run Kang v0.7 compatibility checks.
- Update `docs/EXPERIMENT_LEDGER.md`, `docs/CLAIMS_AND_EVIDENCE.md`, `docs/KNOWN_FAILURES.md`, and `docs/CODEX_SESSION_PROTOCOL.md`.
- Run full regression.
- Commit only after review and passing checks; tag v0.7 only if evidence supports it.

## Files not to commit

- `data/raw/kang_2018_pbmc_ifnb.h5ad`
- `outputs/`
- Python, pytest, and cache artifacts
- Temporary logs, large derived data, and unreviewed experiment outputs

## Rollback point

- Stable rollback tag: `v0.6-real-multicell-lineage-benchmark`
- Do not use `git reset --hard`.
- Do not discard current unstaged or untracked v0.7 work.

## Next exact command

```powershell
python -m pytest tests/test_gene_prior_table.py tests/test_gene_evolution_prior.py tests/test_gene_prior_sources.py tests/test_synthetic_gene_prior.py tests/test_gene_prior_correction_baseline.py tests/test_prior_audit.py
```

## Rescue loop update

- Branch rescue command: `git switch feat/gene-evolutionary-prior-module`
- Branch rescue result: succeeded without stash.
- Current branch after rescue: `feat/gene-evolutionary-prior-module`
- Dirty v0.7 work after rescue: still present.
- Staged changes after rescue: none; `git diff --cached --name-only` returned empty output.
- Raw data and `outputs/`: not staged.

## Targeted v0.7 test update

- Command:
  ```powershell
  python -m pytest tests/test_gene_prior_table.py tests/test_gene_evolution_prior.py tests/test_gene_prior_sources.py tests/test_synthetic_gene_prior.py tests/test_gene_prior_correction_baseline.py tests/test_prior_audit.py
  ```
- Result: passed.
- Pytest summary: `19 passed, 2 warnings in 1.75s`.
- Warnings: two `anndata` deprecation warnings from the local Anaconda environment.
- Fixes made during this loop: none.
- Full regression, synthetic v0.7 runner, commits, and tags were not run.

## Next exact command after this rescue loop

```powershell
git status --short
```

## v0.7 stabilization status check

- Command: `git status --short`
- Command: `git branch --show-current`
- Command: `git diff --stat`
- Current branch: `feat/gene-evolutionary-prior-module`
- Working tree: dirty v0.7 work preserved.
- Staged changes: none; raw data and `outputs/` are not staged.
- Diff stat for tracked files: 2 files changed, 4 insertions, 1 deletion.

## Synthetic sanity-check inspection

- Files inspected: `scripts/run_gene_prior.py`, `configs/experiment/synthetic_v07_gene_prior.yaml`.
- Required weak-base sanity method `gene_prior_correction_control_mean`: present.
- Strong-base correction methods `gene_prior_correction_mean_delta` and `gene_prior_correction_lineage_shrinkage`: present.
- Base methods `control_mean`, `mean_delta`, and `lineage_shrinkage`: present.
- Shuffled negative control: present as `shuffled_gene_prior_correction_lineage`.
- Code changes for this block: none.

## Synthetic v0.7 run

- Command: `python scripts/run_gene_prior.py --config configs/experiment/synthetic_v07_gene_prior.yaml`
- Result: passed.
- Output directory: `outputs/runs/v0.7-gene-evolutionary-prior/synthetic_gene_prior/20260624T004215Z`
- Confirmed outputs: `report.md`, `metrics.csv`, and `prior_audit.md`.
- Confirmed methods in `metrics.csv`: `control_mean`, `mean_delta`, `lineage_shrinkage`, `gene_prior_correction_control_mean`, `gene_prior_correction_mean_delta`, `gene_prior_correction_lineage_shrinkage`, and `shuffled_gene_prior_correction_lineage`.
- Claim boundary: synthetic-only plumbing and ablation logic; not biological evidence.

## Kang v0.7 compatibility run

- Dry-run command: `python scripts/prepare_gene_prior.py --config configs/priors/gene_prior_v07.yaml --dry-run`
- Dry-run result: passed; source mode reported as `synthetic_gene_prior`.
- Kang command: `python scripts/run_gene_prior.py --config configs/experiment/real_v07_kang_gene_prior.yaml`
- Kang result: passed.
- Output directory: `outputs/runs/v0.7-gene-evolutionary-prior/kang_2018_pbmc_ifnb/20260624T004226Z`
- Confirmed outputs: `report.md`, `prior_audit.md`, and `gene_prior_coverage_report.md`.
- Gene-prior source mode in `gene_prior_preparation.json`: `synthetic_gene_prior`.
- Claim boundary: compatibility-only; real evolutionary-prior benefit was not tested.

## Docs sync update

- Updated docs: `README.md`, `docs/PROJECT_SPEC.md`, `docs/DATASETS.md`, `docs/BENCHMARKS.md`, `docs/CLAIMS_AND_EVIDENCE.md`, `docs/EXPERIMENT_LEDGER.md`, `docs/KNOWN_FAILURES.md`, `docs/V07_GENE_EVOLUTIONARY_PRIOR_DESIGN.md`, `docs/V07_GENE_PRIOR_SOURCES.md`, `docs/V07_GENE_PRIOR_ABLATION_PLAN.md`, and this handoff file.
- Main sync result: v0.7 is documented as non-neural gene-prior infrastructure plus synthetic sanity and Kang compatibility-only runs.
- Claim boundary scan: no SOTA, biological-discovery, or real evolutionary-prior benefit claim was added.
- Kang boundary: source mode is `synthetic_gene_prior`; compatibility-only.

## Full regression update

- `python -m pytest`: passed, `93 passed, 2 warnings`.
- Backward compatibility runners passed:
  - `python scripts/run_baseline.py --config configs/experiment/synthetic_v02.yaml`
  - `python scripts/run_real_baseline.py --config configs/experiment/real_v03_baselines.yaml`
  - `python scripts/run_repeated_baselines.py --config configs/experiment/real_v04_repeated_baselines.yaml`
  - `python scripts/run_lineage_prior.py --config configs/experiment/synthetic_v05_lineage.yaml`
  - `python scripts/run_lineage_prior.py --config configs/experiment/real_v05_lineage_compatibility.yaml`
  - `python scripts/run_lineage_real_benchmark.py --config configs/experiment/real_v06_multicell_lineage.yaml`
- New v0.7 commands passed:
  - `python scripts/prepare_gene_prior.py --config configs/priors/gene_prior_v07.yaml --dry-run`
  - `python scripts/run_gene_prior.py --config configs/experiment/synthetic_v07_gene_prior.yaml`
  - `python scripts/run_gene_prior.py --config configs/experiment/real_v07_kang_gene_prior.yaml`
- Final v0.7 synthetic output: `outputs/runs/v0.7-gene-evolutionary-prior/synthetic_gene_prior/20260624T004215Z`
- Final v0.7 Kang output: `outputs/runs/v0.7-gene-evolutionary-prior/kang_2018_pbmc_ifnb/20260624T004226Z`
- Targeted v0.7 ruff: passed after formatting-only fixes.
- Kang source mode: `synthetic_gene_prior`; compatibility-only.
- Commit/tag status at this point: not yet staged, committed, or tagged.

## Staging safety update

- Staging command: `git add README.md configs docs src scripts tests pyproject.toml`
- Staged files are limited to README, configs, docs, scripts, source, and tests.
- Safety check: no staged `data/raw`, `outputs`, cache, or egg-info paths.
- Raw data and generated outputs remain uncommitted.
