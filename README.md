# EvoPrior-AIVC

![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue)
![Tests](https://img.shields.io/badge/tests-164%20passed-brightgreen)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

EvoPrior-AIVC is a reproducible benchmark engineering project for single-cell perturbation-response prediction. The current packaged result is a PCA/Ridge residual baseline evaluated on a public Norman/scPerturb dataset under a fixed internal GEARS-compatible split.

## Result Summary

Dataset: public Norman/scPerturb H5AD, `NormanWeissman2019_filtered.h5ad`  
Expected md5: `c870e6967d91c017d9da827bab183cd6`  
Split: fixed internal GEARS-compatible seen0/seen1/seen2/random_combo split  
Metric status: internal compatible metrics, not official GEARS leaderboard metrics

| model | seeds | MAE | MSE | Pearson | Spearman | status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| v0.14 `weighted_combo_additive` | 1 | 0.5660 | 6.6759 | 0.7599 | 0.6390 | transparent additive baseline |
| v0.15 fast MLP/PCA | 3 | 0.5877 | 7.5517 | 0.7134 | 0.6317 | lightweight trained baseline |
| v0.17 residual baseline | 5 | 0.430778 | 3.668870 | 0.869224 | 0.784976 | five-seed validated baseline |

## Claim Boundary

This repository documents an internal GEARS-compatible Norman benchmark package with a fixed split, data checksum, leakage checks, and a validated residual baseline. It does not claim official GEARS status, leaderboard comparability, SOTA, biological discovery, or broad model superiority beyond the documented split and metric script.

## Quickstart

Install and run no-data checks:

```powershell
python -m pip install -e ".[dev]"
python -m pytest -p no:cacheprovider --basetemp .tmp_pytest_local
python scripts/run_release_smoke.py --config configs/experiment/release_smoke_v019.yaml
```

Run the primary Norman residual baseline after placing the Norman H5AD file locally:

```powershell
python scripts/prepare_gears_norman.py --config configs/data/gears_norman_v013.yaml --dry-run
python scripts/run_norman_residual_multiseed.py --config configs/experiment/gears_norman_v017_multiseed_residual.yaml
python scripts/check_release_artifacts.py
```

Raw data is not committed. Place `NormanWeissman2019_filtered.h5ad` at:

```text
data/raw/NormanWeissman2019_filtered.h5ad
```

## Technical Reading Path

- Technical review map: `docs/TECHNICAL_REVIEW_MAP.md`
- Model card: `docs/V18_RELEASE_MODEL_CARD.md`
- Benchmark card: `docs/V18_BENCHMARK_CARD.md`
- Reproducibility runbook: `docs/V18_REPRODUCIBILITY_RUNBOOK.md`
- External result card: `docs/V17_EXTERNAL_RESULT_CARD.md`
- Public data acquisition guide: `docs/V21_PUBLIC_DATA_ACQUISITION_GUIDE.md`
- Known failures and limitations: `docs/KNOWN_FAILURES.md`

## Data And GEARS Status

The validated result uses an internal GEARS-compatible Norman split. Official GEARS execution remains blocked in the recorded environment, so this repository does not report official GEARS metrics.

## Repository Scope

This repository should keep public technical artifacts only: source code, configs, tests, model cards, benchmark cards, reproducibility documentation, and small audit reports.

## License

MIT License. See `LICENSE`.
