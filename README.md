# EvoPrior-AIVC

![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue)
![Tests](https://img.shields.io/badge/tests-164%20passed-brightgreen)
![License](https://img.shields.io/badge/license-MIT-lightgrey)
![Benchmark](https://img.shields.io/badge/benchmark-internal%20GEARS--compatible%20Norman-informational)

EvoPrior-AIVC is a reproducible research-engineering repository for single-cell perturbation-response prediction. The current documented result is a validated residual baseline on a public Norman/scPerturb H5AD under a fixed internal GEARS-compatible split, with locked data provenance, split policy, metrics, model card, benchmark card, and reproduction commands.

## Current Result

Dataset: `NormanWeissman2019_filtered.h5ad` from scPerturb Zenodo record 13350497, version 1.4. Expected md5: `c870e6967d91c017d9da827bab183cd6`.

Split: fixed internal GEARS-compatible Norman seen0/seen1/seen2/random_combo split. Metrics below are internal compatible metrics, not official GEARS leaderboard metrics.

| model | MAE | MSE | Pearson delta | Spearman logFC | status |
| --- | ---: | ---: | ---: | ---: | --- |
| `weighted_combo_additive` | 0.5660 | 6.6759 | 0.7599 | 0.6390 | transparent additive baseline |
| fast MLP/PCA | 0.5877 | 7.5517 | 0.7134 | 0.6317 | lightweight trained baseline |
| residual baseline | 0.430778 | 3.668870 | 0.869224 | 0.784976 | five-seed validated internal result |

## Claim Boundary

Allowed: "A validated residual baseline on a public Norman/scPerturb H5AD under a fixed internal GEARS-compatible split."

Not allowed:

- official GEARS result
- official leaderboard comparability
- SOTA claim
- biological discovery claim
- clinical-use claim
- broad model-superiority claim
- claim that evolutionary or conservation priors provide general benefit

## Installation

```powershell
python -m pip install -e ".[dev]"
```

The package requires Python 3.10 or newer. The default development checks use `pytest` and `ruff`.

## Quickstart: No-Data Smoke Test

This path does not require the Norman H5AD file.

```powershell
python -m pytest -p no:cacheprovider --basetemp .tmp_pytest_local tests/test_release_smoke_config.py tests/test_release_artifact_manifest.py tests/test_ci_workflow_static.py
python scripts/run_release_smoke.py --config configs/experiment/release_smoke_v019.yaml
python scripts/check_release_artifacts.py
```

On Windows, the repository-local `--basetemp` avoids host temp-directory permission issues.

## With-Data Reproduction

Place the legally obtained file at:

```text
data/raw/NormanWeissman2019_filtered.h5ad
```

Verify the expected md5 checksum:

```text
c870e6967d91c017d9da827bab183cd6
```

Run:

```powershell
python scripts/prepare_gears_norman.py --config configs/data/gears_norman_v013.yaml --dry-run
python scripts/run_norman_residual_multiseed.py --config configs/experiment/gears_norman_v017_multiseed_residual.yaml
python scripts/check_release_artifacts.py
```

Reference output path:

```text
outputs/runs/v0.17-norman-validated-residual-baseline/gears_norman_scperturb_v013/20260625T100322Z/
```

Generated run outputs are not committed.

## Repository Structure

```text
configs/      Experiment and data configuration files
src/          Python package source
scripts/      Reproduction and utility scripts
tests/        Unit and smoke tests
docs/         Stable technical documentation
reports/      Small tracked summaries and manifests only
data/         Empty placeholders only; raw data is not committed
outputs/      Empty placeholders only; generated outputs are ignored
```

## Core Documentation

- Model card: `docs/MODEL_CARD.md`
- Benchmark card: `docs/BENCHMARK_CARD.md`
- Reproducibility runbook: `docs/REPRODUCIBILITY.md`
- Data policy and acquisition: `docs/DATA.md`
- Known limitations: `docs/KNOWN_LIMITATIONS.md`
- Experiment ledger: `docs/EXPERIMENT_LEDGER.md`
- Claims and evidence: `docs/CLAIMS_AND_EVIDENCE.md`

Historical operational notes and publication logistics, when retained, live under `docs/archive/internal/` and are not part of the public technical documentation.

## Data Policy

Raw data is not committed. Public data must be obtained legally from the documented source and verified locally by checksum. The tracked `data/` and `outputs/` directories contain placeholders only; generated outputs and large artifacts are ignored.

## Limitations

- The Norman benchmark uses an internal GEARS-compatible split, not the exact official GEARS split.
- Metrics are internal compatible metrics, not official leaderboard metrics.
- The official GEARS wrapper remains feasibility-only in this repository.
- The current validated result is single-dataset and split-specific.
- The repository does not provide biological discovery or clinical evidence.

## Citation And License

See `CITATION.cff` for citation metadata and `LICENSE` for the MIT license.
