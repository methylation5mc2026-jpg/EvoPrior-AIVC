# Known Limitations

## Benchmark Alignment

- The Norman benchmark uses an internal GEARS-compatible split, not exact official GEARS split files.
- Metrics are internal compatible metrics, not official GEARS leaderboard metrics.
- The official GEARS wrapper is feasibility-only and does not train or evaluate official GEARS.

## Scope

- The validated result is single-dataset and split-specific.
- Norman is a limited context for broad biological, cell-type, donor, tissue, or clinical generalization.
- The result should not be interpreted as SOTA or broad model superiority.

## Priors

- The repository includes lineage and gene-prior engineering modules, but the current public Norman result should not be presented as proof of general evolutionary or conservation-prior benefit.
- HGNC metadata features are coarse gene metadata, not orthology, conservation score, or gene-age evidence.

## Data And Outputs

- Raw data is not committed.
- Full reproduction requires legal local data acquisition and checksum verification.
- Generated outputs are ignored except for small tracked summaries and manifests.

## Scientific Claims

Do not claim:

- official GEARS result
- leaderboard comparability
- SOTA
- biological discovery
- clinical utility
- general model superiority
