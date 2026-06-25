# v0.13 GEARS/Norman Baseline

## Executive Summary

v0.13 executes a reproducible GEARS-compatible internal baseline run on the public Norman/scPerturb H5AD. The selected dataset is `NormanWeissman2019_filtered.h5ad` from scPerturb Zenodo record 13350497, version 1.4. The local file checksum is md5 `c870e6967d91c017d9da827bab183cd6`.

This is not an official GEARS leaderboard run. The exact official GEARS split files and official metric package are not imported.

## Source And Access

- Source: <https://zenodo.org/records/13350497>
- Source version: scPerturb Zenodo record v1.4
- File: `NormanWeissman2019_filtered.h5ad`
- License: CC-BY-4.0 via Zenodo record
- Expected size: 698,680,199 bytes
- Expected md5: `c870e6967d91c017d9da827bab183cd6`
- Local path: `data/raw/NormanWeissman2019_filtered.h5ad`
- Data config: `configs/data/gears_norman_v013.yaml`

Raw data is not committed to git.

## Commands

```powershell
python scripts/prepare_gears_norman.py --config configs/data/gears_norman_v013.yaml --dry-run
python scripts/prepare_gears_norman.py --config configs/data/gears_norman_v013.yaml
python scripts/run_gears_norman_baseline.py --config configs/experiment/gears_norman_v013_baseline.yaml
```

## Latest Output

```text
outputs/runs/v0.13-gears-norman-baseline/gears_norman_scperturb_v013/20260625T002742Z/
outputs/data_reports/gears_norman_scperturb_v013/20260625T002742Z/
```

Key files:

- `report.md`
- `metrics.csv`
- `per_class_metric_summary.csv`
- `de_summary.csv`
- `split_manifest.csv`
- `split_leakage_audit.json`
- `benchmark_evidence.json`
- `benchmark_evidence_table.csv`
- `benchmark_evidence_report.md`

## Schema Mapping

- Adapter: `src/evoprior_aivc/data/gears_norman_adapter.py`
- Perturbation field candidates include `perturbation`, `condition`, `gene`, `target`, `guide_target`, and `guide_identity`.
- Canonical fields include `perturbation`, `is_control`, `perturbation_genes`, `perturbation_type`, and `cell_type`.
- Observed local H5AD shape from backed inspection: 111,445 cells x 33,694 genes.

## Split

- Split mode: `gears_compatible_combo`
- Official status: GEARS-compatible/internal, not official GEARS.
- Split seed: `1300`
- Test groups: 33 combo and 31 single groups.
- Test classes: seen0=2, seen1=13, seen2=18, single_unseen=31.
- Leakage audit: passed; leaked test combos: none.

## Baselines

- `no_change`
- `control_mean`
- `mean_delta`
- `perturbation_mean_delta_v2`
- `single_effect_additive_combo`
- `ridge_cv`
- `evoprior_additive_no_prior`

`single_effect_additive_combo` predicts combo effects by summing available single-gene perturbation deltas, with a documented fallback for missing singles.

## Main Test Metrics

| Baseline | MAE | MSE | Pearson delta | Spearman logFC |
| --- | ---: | ---: | ---: | ---: |
| `control_mean` | 0.8739 | 13.4469 | NA | NA |
| `mean_delta` | 0.5939 | 7.6769 | 0.6450 | 0.4920 |
| `single_effect_additive_combo` | 0.5491 | 6.1062 | 0.7538 | 0.5583 |

Combo-only test metrics for `single_effect_additive_combo`:

- MAE 0.5938
- MSE 6.5080
- Pearson delta 0.8218
- Spearman logFC 0.6388

## Claim Boundary

Allowed:

- A reproducible public Norman/scPerturb GEARS-compatible internal baseline run was executed.
- The data source, checksum, split, command, metric script, and output directory are documented.
- `single_effect_additive_combo` is strongest among implemented transparent baselines under this exact internal split.

Forbidden:

- SOTA.
- Official GEARS result.
- Leaderboard comparability.
- Neural GEARS reproduction.
- Biological discovery.
- General EvoPrior superiority.
