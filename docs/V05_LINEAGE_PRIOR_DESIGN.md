# v0.5 Lineage Prior Design

Status: implemented first prior module. This document defines the claim boundary for v0.5.

## Scientific Hypothesis

Cell-type perturbation responses are not independent across flat labels. Related cell types may share perturbation response components due to developmental lineage, functional similarity, shared regulatory programs, or historical constraints.

The v0.5 hypothesis is intentionally narrow:

- A lineage-aware baseline should be able to borrow perturbation response information from related training cell types.
- This should be visible on a synthetic benchmark where the lineage structure and response generation process are known.
- This should not be claimed as real biological improvement unless a real multi-cell-type dataset with meaningful lineage structure is evaluated.

## Computational Abstraction

Represent cell types as nodes in a rooted tree:

```text
root
|-- immune
|   |-- myeloid
|   |-- lymphoid
|-- epithelial
|-- stromal
```

The implementation supports a simple tree with:

- node identifiers,
- parent-child edges,
- depths,
- ancestors and descendants,
- lowest common ancestor,
- tree distance,
- distance-derived relatedness kernels,
- clade membership features.

## Response Decomposition

The v0.5 synthetic generator and baseline follow:

```text
delta =
    global perturbation response
  + lineage-shared effect
  + cell-type-specific effect
  + residual noise
```

This is not yet the full EvoPrior neural decomposition. It is a non-neural infrastructure and sanity-check baseline.

## v0.5 Baseline

`LineageShrinkageBaseline` predicts a perturbation delta for a target cell type by combining:

- direct perturbation mean if available,
- lineage-distance weighted perturbation response from related training cell types,
- global perturbation mean fallback,
- zero/global fallback for unseen perturbations depending on configuration.

Weights use:

```text
weight(c_train, c_target) = exp(-tree_distance(c_train, c_target) / tau)
```

The baseline must:

- fit only on training groups,
- never use target post-perturbation expression,
- handle unknown cell types explicitly,
- degrade safely on single-cell-type data,
- report no-op/fallback behavior when lineage signal is not identifiable.

## Allowed Claims

- Lineage tree infrastructure is implemented and tested.
- Cell-type-to-lineage mapping is implemented and tested.
- Lineage distance, relatedness kernel, and clade features are implemented and tested.
- A lineage-aware non-neural baseline is implemented and tested.
- A synthetic lineage benchmark validates expected plumbing under known lineage-structured response generation.
- Papalexi compatibility check confirms graceful no-op/fallback behavior on a single-cell-type dataset.

## Forbidden Claims

- Lineage prior improves real biological prediction on Papalexi.
- EvoPrior neural model works.
- Evolutionary priors improve prediction.
- SOTA or near-SOTA performance.
- Generalization to real multi-cell-type settings.
- Biological discovery.

## Rollback

The rollback point for v0.5 is tag `v0.4-real-baseline-strengthening`.
