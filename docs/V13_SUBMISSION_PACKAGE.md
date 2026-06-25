# v0.13 Submission Package

## Package Scope

This package is a reviewer-facing local artifact bundle for v0.13. It supports inspection of a reproducible GEARS-compatible internal baseline run on public Norman/scPerturb data.

It is not a leaderboard submission package.

## Source

- Dataset: `NormanWeissman2019_filtered.h5ad`
- Source: <https://zenodo.org/records/13350497>
- Version: scPerturb Zenodo record v1.4
- License: CC-BY-4.0 via Zenodo record
- md5: `c870e6967d91c017d9da827bab183cd6`
- Data config: `configs/data/gears_norman_v013.yaml`

## Reproduction Commands

```powershell
python scripts/prepare_gears_norman.py --config configs/data/gears_norman_v013.yaml --dry-run
python scripts/prepare_gears_norman.py --config configs/data/gears_norman_v013.yaml
python scripts/run_gears_norman_baseline.py --config configs/experiment/gears_norman_v013_baseline.yaml
```

## Artifact Directory

```text
outputs/runs/v0.13-gears-norman-baseline/gears_norman_scperturb_v013/20260625T002742Z/
```

## Required Files For Reviewer

- `report.md`
- `run_manifest.json`
- `resolved_config.yaml`
- `resolved_data_config.yaml`
- `dataset_preparation.json`
- `schema_report.md`
- `split_report.md`
- `split_manifest.csv`
- `split_leakage_audit.json`
- `metrics.csv`
- `metric_summary.csv`
- `per_perturbation_metrics.csv`
- `per_class_metric_summary.csv`
- `de_summary.csv`
- `combo_additive_fallbacks.csv`
- `benchmark_evidence_report.md`
- `benchmark_evidence_table.csv`

## Main Result Snapshot

| Baseline | Test MAE | Test MSE | Test Pearson | Test Spearman |
| --- | ---: | ---: | ---: | ---: |
| `control_mean` | 0.8739 | 13.4469 | NA | NA |
| `mean_delta` | 0.5939 | 7.6769 | 0.6450 | 0.4920 |
| `single_effect_additive_combo` | 0.5491 | 6.1062 | 0.7538 | 0.5583 |

## Review Checklist

- Data checksum is present and `ok`.
- Split report documents internal GEARS-compatible status.
- Leakage audit passes with no leaked test combos.
- Metrics are labeled internal compatible metrics.
- Raw H5AD and outputs are not committed.
- Claims exclude SOTA, leaderboard, official GEARS, neural GEARS, and biological discovery.

## Next Milestone Boundary

The next milestone may pursue official GEARS split alignment or a fast neural baseline. That work is not included in v0.13.
