# v0.6 Lineage Real Benchmark Design

Status: implementation design for the Kang 2018 PBMC IFN-beta benchmark.

Main run output:

```text
outputs/runs/v0.6-real-multicell-lineage-benchmark/kang_2018_pbmc_ifnb/20260623T092131Z/
```

## Scientific Question

Can the v0.5 non-neural `LineageShrinkageBaseline` borrow IFN-beta response information from related PBMC cell types better than v0.4-style classical baselines under leakage-safe held-out cell-type splits?

This is a narrow real-data benchmark. It does not ask whether lineage priors generally work, and it does not evaluate a neural EvoPrior model.

## Dataset

- Dataset ID: `kang_2018_pbmc_ifnb`
- Data: Kang et al. 2018 PBMC IFN-beta stimulation H5AD.
- Conditions: `ctrl` and `stim`.
- Cell types after normalization: `cd4_t_cells`, `cd8_t_cells`, `b_cells`, `nk_cells`, `cd14_monocytes`, `fcgr3a_monocytes`, `dendritic_cells`, `megakaryocytes`.
- Donor-like field: `replicate`.
- Main run schema report: `outputs/data_reports/kang_2018_pbmc_ifnb/20260623T092131Z/schema_report.md`.

## Lineage Mapping

The v0.6 prior is a coarse operational hematopoietic tree:

```text
root
└── hematopoietic
    ├── lymphoid
    │   ├── t_cells
    │   │   ├── cd4_t_cells
    │   │   └── cd8_t_cells
    │   ├── b_cells
    │   └── nk_cells
    ├── myeloid
    │   ├── monocytes
    │   │   ├── cd14_monocytes
    │   │   └── fcgr3a_monocytes
    │   └── dendritic_cells
    └── megakaryocytic
        └── megakaryocytes
```

This tree is not an ontology-grade lineage assertion. It is a documented operational prior for benchmark distance weighting and clade-level diagnostics.

## Control Policy

The main split mode is `control_observed_ood`:

- held-out cell-type stimulated pseudobulks are test targets only;
- held-out cell-type control pseudobulks may be used as input control expression;
- held-out cell-type stimulated deltas are never used for training or validation;
- this matches common perturbation prediction settings where the unperturbed target state is observed.

Strict OOD mode, where no held-out cell-type data at all is used in training or as control input, is harder for the current delta-dataset API and is not the default v0.6 run. It can be added later if a global-control reconstruction path is implemented and validated.

## Split Design

Primary suite: `heldout_cell_type_suite`.

Eligibility:

- each held-out cell type must have at least one control pseudobulk and one stimulated pseudobulk after filtering;
- each held-out cell type should have at least 3 test groups when donor-level grouping permits;
- training must contain both `ctrl` and `stim` for other cell types;
- held-out stimulated groups are absent from train and validation;
- skipped cell types are written to `skipped_cell_types.csv`.

Optional suite: `heldout_lineage_suite`.

- `lymphoid` and `myeloid` are candidate clades.
- This is run only if enough non-held-out training cell types and test groups remain.
- If underpowered, clade split is skipped and documented.

## Baselines

v0.4 baselines:

- `control_mean`
- `mean_delta`
- `perturbation_mean_delta_v2`
- `hierarchical_additive`
- `ridge_cv`

v0.5 prior baseline:

- `lineage_shrinkage`

All baselines use the same pseudobulk table, same split labels, same metrics, and same held-out cell-type targets.

## Metrics

- MAE and MSE over delta expression.
- Pearson and Spearman delta correlation when finite.
- DE recovery over top-k absolute delta genes.
- Per-held-out-cell-type summaries.
- Confidence intervals where at least 3 held-out cell-type results support the interval.

Retrieval/PDS is optional and may be skipped because Kang has only one non-control perturbation, making perturbation retrieval largely uninformative.

## v0.6 Result Summary

Primary held-out cell-type suite:

- 7 eligible held-out cell types.
- `megakaryocytes` skipped because it has too few test groups.
- `lineage_shrinkage` mean MAE: 0.3160.
- `mean_delta` / `hierarchical_additive` mean MAE: 0.4317.
- `control_mean` mean MAE: 0.4221.
- `ridge_cv` mean MAE: 0.4969.
- `lineage_shrinkage` mean Pearson: 0.7399.

Held-out lineage suite:

- `lymphoid` and `myeloid` clade splits ran.
- n=2; all CI rows are underpowered.
- Treat lineage-suite results as diagnostic only.

Tau audit:

- Pre-specified tau values 0.5, 1.0, 2.0, 4.0 were reported separately.
- The audit is sensitivity-only and does not select a tuned tau.

## Claim Boundary

Allowed:

- v0.6 evaluates a lineage-aware non-neural baseline on one real multi-cell-type PBMC IFN-beta dataset.
- On this dataset and split, lineage-aware shrinkage did or did not outperform named baselines on named metrics.
- The result is preliminary and dataset-specific.

Forbidden:

- lineage priors generally work;
- EvoPrior achieves SOTA;
- evolutionary history improves AIVC;
- this is public-leaderboard comparable;
- one-stimulation PBMC results generalize to many perturbation types.
