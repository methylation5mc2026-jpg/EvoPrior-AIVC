# v0.7 Gene Prior Sources

Status: source policy and supported modes for v0.7.

## Supported Modes

### Mode A: Synthetic / Toy Gene Prior Table

Purpose:

- unit tests,
- synthetic v0.7 benchmark,
- engineering compatibility checks.

Rules:

- source must be recorded as `synthetic_gene_prior`;
- source version must be recorded;
- synthetic success is logic validation only;
- synthetic/toy prior must not be used for real biological claims.

### Mode B: Local / Manual Gene Prior CSV

Purpose:

- preferred path for reproducible real ablations.

Rules:

- CSV path is configured by YAML;
- required ID column is `gene_symbol` or `gene_id`;
- checksum is recorded in the manifest;
- large local feature tables are not committed;
- feature meanings, source version, and missing-value behavior must be documented.

### Mode C: Optional External Annotation Downloader

Purpose:

- future stable small annotation sources.

Rules:

- only allowed when URL, source version, date, and checksum are recorded;
- download must fail gracefully if unavailable;
- no test may require internet;
- no external source is mandatory for core tests.

Potential future resources:

- Ensembl Compara / BioMart homology or ortholog counts,
- OrthoDB hierarchical ortholog groups,
- Gene Ontology annotations or GO-slim categories,
- curated gene age / phylostratigraphy tables.

## v0.7 Kang Source Decision

No stable, small, versioned, biologically meaningful gene-prior annotation source is bundled with this repository in v0.7.

Therefore the real Kang run uses an engineering-only synthetic/placeholder prior table generated deterministically from the Kang gene list to validate mapping, coverage, missing-feature behavior, and runner compatibility.

This means:

- Kang real evolutionary-prior benefit is **not** scientifically tested in v0.7.
- The Kang run is compatibility-only.
- Claims about evolutionary priors must rely only on synthetic logic validation until a versioned real gene-prior CSV is supplied.

Executed v0.7 compatibility output:

```text
outputs/runs/v0.7-gene-evolutionary-prior/kang_2018_pbmc_ifnb/20260624T004226Z/
```

## Generated Feature Table Policy

Generated feature tables are written under:

```text
data/interim/gene_priors/<prior_id>/
```

Files:

- `gene_prior_features.csv`
- `manifest.json`

These are local/interim artifacts and are not committed unless intentionally tiny fixtures.
