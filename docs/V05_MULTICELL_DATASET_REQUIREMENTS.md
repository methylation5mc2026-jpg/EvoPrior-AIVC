# v0.5/v0.6 Real Multi-Cell-Type Dataset Requirements

Status: requirements record. v0.6 selected Kang 2018 PBMC IFN-beta as the first real multi-cell-type lineage benchmark, with limitations.

## Minimum Requirements

A real dataset suitable for evaluating cell-lineage priors should have:

- at least 3 cell types,
- preferably multiple related cell types in one biological family,
- clear perturbation labels,
- clear control labels,
- enough cells per `cell_type x perturbation` group for pseudobulk aggregation,
- multiple perturbations shared across several cell types,
- manageable local size,
- documented source, license, and checksum,
- an explicit benchmark split if available.

## Preferred Requirements

Stronger candidates should also include:

- donor metadata,
- batch metadata,
- tissue or condition metadata,
- multiple related immune or developmental cell states,
- a published preprocessing recipe,
- known public baseline results,
- held-out cell-type or held-out lineage split definitions.

## Why Papalexi Is Insufficient

The current v0.3/v0.4 real dataset, `scperturb_papalexi_2021_arrayed_rna`, has one cell type/cell line in the configured H5AD. It remains valuable for real-data plumbing and baseline hardening, but it cannot identify whether a lineage prior helps, because there are no related cell types to borrow from.

## v0.6 Outcome

v0.6 selected `kang_2018_pbmc_ifnb`.

It satisfies the minimum multi-cell-type gate:

- 8 PBMC cell types,
- `ctrl` and `stim` labels,
- donor-like `replicate` metadata,
- public H5AD file under 2 GB,
- md5 checksum available,
- control-observed held-out cell-type split is feasible for 7 cell types.

It does not satisfy the stronger multiple-perturbation preference because it has only one non-control condition, IFN-beta stimulation. Therefore v0.6 claims must remain dataset-specific and preliminary.
