# v0.4 Baseline Audit

Status: initial v0.4 audit before adding stronger baselines and repeated evaluation.

## Claim Boundary

Allowed engineering claims:

- The real-data baseline loop can ingest one public H5AD perturbation dataset.
- Canonical schema mapping, pseudobulk aggregation, leakage checks, and classical baselines run under documented configs.
- Classical baselines can be compared under one documented project-defined split.

Not allowed:

- SOTA or near-SOTA.
- Biological discovery.
- EvoPrior effectiveness.
- Evolutionary, lineage, or pathway prior benefit.
- Generalization to other datasets.
- Comparison to published papers unless preprocessing, split, and metrics are matched.

## Dataset Summary

Dataset ID: `scperturb_papalexi_2021_arrayed_rna`

- Source: scPerturb Zenodo v1.4.
- File: `PapalexiSatija2021_eccite_arrayed_RNA.h5ad`.
- md5: `843820d48b024348d6132cd53be0da91`.
- Cells: 8,984.
- Genes before filtering: 16,826.
- Genes after v0.3 filtering: 3,000.
- Perturbations observed before pseudobulk filtering: 11 including control.
- Controls: 2,009 cells.
- Cell types: one canonical `monocytes` label.
- Donor: unavailable.
- Batch: unavailable.

## Pseudobulk Summary

v0.3 grouping:

- `cell_type`
- `perturbation`
- `guide_id`

v0.3 threshold:

- `min_cells_per_group = 20`

Observed after filtering:

- Pseudobulk groups: 13.
- Delta examples: 11 non-control groups.
- Minimum group cells: 24.
- Maximum group cells: 1,023.
- Median group cells: 750.

Warnings:

- `IFNGR2` has only 4 cells and is dropped.
- `PDL1g2` has 24 cells and is retained only because v0.3 reduced the threshold from 25 to 20.
- Pseudobulk groups are guide-level, not donor-level or replicate-level.
- There is no donor or batch axis to estimate biological replicate uncertainty.

## Split Summary

`random_group`:

- Engineering sanity split at pseudobulk group level.
- Not a biological benchmark.
- With only 11 delta examples, train/val/test composition is highly unstable.

`heldout_perturbation:pdl1`:

- `pdl1` is held out from train/val.
- `pdl1` was selected because it has two retained guide-level pseudobulk groups after `min_cells_per_group = 20`.
- This is still statistically underpowered and should be interpreted as a plumbing stress test.

## Preprocessing Summary

Current v0.3 choices:

- Use active `X` from the H5AD.
- Filter genes expressed in fewer than 10 cells.
- Select top 3,000 genes by variance.
- Pseudobulk mean aggregation.

Unresolved:

- The project has not reproduced upstream scPerturb QC.
- It has not verified whether active `X` is raw counts, normalized counts, or log-normalized values.
- It has not matched Papalexi, pertpy, GEARS, scGen, CPA, or Virtual Cell Challenge preprocessing.

## Baseline Summary

v0.3 baselines:

- `no_change`: predicts zero delta.
- `mean_delta`: seen perturbation mean delta; unseen fallback to global mean.
- `additive`: global mean plus perturbation and cell-type offsets.
- `ridge`: control expression plus one-hot metadata.

Expected failure modes:

- `no_change` ignores perturbation response entirely.
- `mean_delta` fails on unseen perturbations except via global fallback.
- `additive` collapses to a simple mean model when only one cell type exists.
- `ridge` is underdetermined with very few pseudobulk groups and many genes.

## v0.4 Motivation

v0.4 should not add novelty. It should strengthen the baseline layer by adding:

- explicit control-mean and hierarchical additive baselines,
- ridge alpha selection,
- repeated split evaluation,
- confidence intervals with underpowered warnings,
- perturbation retrieval metrics,
- DE recovery metrics,
- preprocessing sensitivity checks,
- public benchmark alignment audit.

