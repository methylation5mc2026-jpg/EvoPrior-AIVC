# v0.7 Gene Evolutionary Prior Design

Status: v0.7 design and claim-boundary document.

## Scientific Hypothesis

Genes are not interchangeable output coordinates. They differ in evolutionary age, conservation, orthology breadth, functional constraint, pathway membership, expression breadth, and context specialization.

Perturbation-response prediction may benefit from distinguishing:

- ancient/core/conserved genes,
- lineage-specific or immune-specialized genes,
- broadly expressed housekeeping genes,
- context-specific response genes,
- genes with missing or uncertain prior annotations.

The v0.7 hypothesis is intentionally narrow:

- gene-prior features can provide a gene-level modulation or residual correction signal;
- this can be validated first on synthetic data where the gene-prior structure is known;
- real Kang PBMC IFN-beta evaluation is only meaningful if the gene-prior source is versioned and biologically meaningful;
- if only synthetic/placeholder priors are available, Kang is compatibility-only.

## Response Decomposition

```text
delta_gene =
    cell-lineage component
  + perturbation component
  + gene-prior modulation
  + residual
```

v0.7 does not implement a neural EvoPrior model. It adds a versioned gene-prior substrate plus a simple non-neural correction layer.

## Gene-Prior Features

Supported fields are optional and validated when present:

- `conservation_score`: larger means more conserved or constrained.
- `gene_age_rank`: smaller may represent older genes depending on source convention; config/docs must state convention.
- `ortholog_count`: number or breadth of detected orthologs.
- `paralog_count`: number of paralogs.
- `expression_breadth`: how broadly expressed a gene is across tissues/cell types.
- `is_housekeeping`: binary housekeeping indicator.
- `is_immune_related`: binary immune/context annotation.
- `go_slim_category`: coarse GO-slim category.
- `pathway_category`: coarse pathway category.

Every feature table must record `source` and `source_version`. External or local files should also have a checksum in the manifest.

## Leakage Rule

Gene-prior features must be independent of target perturbation response labels.

Forbidden:

- computing gene-prior features from test-set deltas,
- selecting prior features by test performance,
- using held-out target response to construct annotations,
- calling synthetic/placeholder annotations biological evidence.

Allowed:

- using versioned external annotations,
- using local manual CSV annotations with checksum,
- using synthetic/toy prior tables for tests and synthetic benchmarks,
- using placeholder/synthetic Kang prior only for engineering compatibility if clearly labeled.

## Allowed Claims In v0.7

- Gene-prior table infrastructure is implemented and tested.
- Gene-prior correction baseline is implemented and tested.
- Synthetic gene-conservation benchmark validates plumbing and ablation logic.
- Kang gene-prior feature mapping and coverage are reported as compatibility-only when using placeholder priors.
- Gene-prior correction is compared against base baselines.
- Real evolutionary-prior benefit is not tested unless a meaningful, versioned biological gene-prior source is configured.

## Forbidden Claims In v0.7

- SOTA or near-SOTA.
- General evolutionary-prior effectiveness.
- Biological discovery.
- Causal evolutionary explanation.
- Public leaderboard comparability.
- Neural EvoPrior effectiveness.

## Rollback

Rollback point: `v0.6-real-multicell-lineage-benchmark`.
