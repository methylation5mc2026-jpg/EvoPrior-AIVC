# v0.13 Benchmark Alignment Audit

## Decision

Selected benchmark: `gears_norman_scperturb_v013`

Decision: run now as GEARS-compatible/internal.

## Candidate Table

| benchmark_id | source | official or compatible | dataset | access | blocker | decision |
| --- | --- | --- | --- | --- | --- | --- |
| `gears_norman_scperturb_v013` | scPerturb Zenodo 13350497 | GEARS-compatible/internal | `NormanWeissman2019_filtered.h5ad` | public H5AD, md5 locked | exact official GEARS split files not imported | run now |
| `scperturb_papalexi_2021_arrayed_rna_v012` | scPerturb Zenodo 13350497 | custom benchmark-compatible | Papalexi/Satija ECCITE-seq RNA | local/public H5AD | underpowered n=2 held-out perturbations | regression only |
| `kang_2018_pbmc_ifnb` | Figshare / pertpy-compatible | project-defined | Kang PBMC IFN-beta | local/public H5AD | not a public perturbation-prediction benchmark split | regression only |

## Alignment Status

- Data source: public scPerturb H5AD.
- Data version: Zenodo record 13350497, version 1.4.
- File checksum: md5 `c870e6967d91c017d9da827bab183cd6`.
- Split: internally generated GEARS-compatible combo split with seen0/seen1/seen2 labels.
- Metrics: internal compatible MAE, MSE, Pearson delta, Spearman logFC, DE20/DE50 recovery.

## Not Official GEARS

This run cannot claim official GEARS alignment because:

- exact official GEARS split files are not imported;
- exact official GEARS preprocessing is not reproduced;
- exact official GEARS metric package is not imported;
- no neural GEARS model is trained or evaluated.

## Leakage Audit

Latest output:

```text
outputs/runs/v0.13-gears-norman-baseline/gears_norman_scperturb_v013/20260625T002742Z/split_leakage_audit.json
```

Summary:

- overall pass: true;
- leaked test combos: none;
- test combo groups: 33;
- test split classes: seen0=2, seen1=13, seen2=18.

## External Claim Status

Externally safe:

- "We executed a reproducible GEARS-compatible internal baseline run on public Norman/scPerturb data."
- "The strongest implemented transparent baseline in this run was `single_effect_additive_combo` under the documented split."

Not safe:

- official GEARS result;
- leaderboard result;
- SOTA;
- neural GEARS reproduction;
- biological discovery;
- general EvoPrior superiority.
