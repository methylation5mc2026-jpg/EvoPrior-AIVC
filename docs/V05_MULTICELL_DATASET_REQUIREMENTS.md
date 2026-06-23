# v0.5/v0.6 Real Multi-Cell-Type Dataset Requirements

Status: requirements for future real lineage-prior validation. v0.5 does not use this document to claim real biological improvement.

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

## Future v0.6 Target

v0.6 should select a real multi-cell-type perturbation dataset and compare v0.4 baselines against v0.5 lineage-aware baselines under held-out cell-type or held-out lineage splits.

