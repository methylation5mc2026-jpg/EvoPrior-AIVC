# v0.8 Real Gene Prior Source Design

Status: source decision and reproducibility plan for `v0.8-real-versioned-gene-prior-source`.

## Decision Summary

v0.8 uses the HGNC complete set as the first real, versioned source for a reproducible human gene-prior table. This is a real functional/gene-metadata prior, not a real evolutionary or conservation prior, because no orthology, conservation score, or gene-age source is configured.

Primary source:

- HGNC complete set TSV: `https://storage.googleapis.com/public-download-files/hgnc/tsv/tsv/hgnc_complete_set.txt`
- HGNC download page: `https://www.genenames.org/download/statistics-and-files/`
- HGNC license page: `https://www.genenames.org/about/license/`

Optional source supported by adapter, but not required for v0.8 success:

- GOA human GAF: `https://current.geneontology.org/annotations/goa_human.gaf.gz`
- GO annotation downloads: `https://current.geneontology.org/products/pages/downloads.html`
- GAF format: `https://geneontology.org/docs/go-annotation-file-gaf-format-2.1/`

## Source Decision Table

| Layer | Source | URL/manual note | Format | Approx size | License/access | Version/date | Checksum | Feature columns | Risk | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | HGNC complete set | Official HGNC Google Storage TSV | TSV | HGNC page listed 16.1 MB on 2026-06-19 | HGNC says data are CC0/public-domain style reuse | current page date 2026-06-19; manifest records checksum | md5 and sha256 recorded locally | `approved_symbol_present`, `gene_biotype`, `locus_group`, `hgnc_gene_group_count`, `is_immune_related` | current file can update; checksum captures prepared snapshot | Use for v0.8 |
| B | GOA human GAF | Official GOA human GAF | gzip GAF 2.x | GO page listed 906455 annotations for 2026-05-19 release | GO page lists CC-BY 4.0 terms | 2026-05-19 release page | md5 and sha256 recorded if used | `go_annotation_count`, `go_bp_count`, `go_mf_count`, `go_cc_count`, optional immune keyword flag | larger file; no GO-slim ontology bundled | Adapter only in v0.8 |
| C | Curated local CSV | User-provided file with explicit source/version/checksum | CSV | user-defined | user-defined | user-defined | md5 and sha256 recorded | may include `ortholog_count`, `conservation_score`, `gene_age_rank`, `one_to_one_ortholog_flag` | can be high quality or weak depending on provenance | Supported, not bundled |
| C optional | Ensembl/OrthoDB-like orthology | local CSV only in v0.8 | CSV | user-defined | user-defined | user-defined | md5 and sha256 recorded | orthology/conservation features | no stable small automatic source selected | Defer automatic download |

## Feature Semantics

- `approved_symbol_present`: 1 when an HGNC approved symbol record exists.
- `gene_biotype`: HGNC `locus_type`, categorical.
- `locus_group`: HGNC `locus_group`, categorical.
- `hgnc_gene_group_count`: number of HGNC gene-group annotations.
- `is_immune_related`: coarse keyword flag from HGNC gene group/name/locus text. It is a functional metadata feature, not a discovery claim.
- GO count features are only present when a GOA GAF source is configured.
- Orthology/conservation features are only present when a curated source supplies them.

## Claim Boundary

Allowed:

- HGNC/GOA/local source adapters are implemented and tested.
- The generated table is versioned by source URL/path, source version note, preparation time, md5, sha256, row count, feature columns, and git hash.
- Kang v0.8 can be described as a real HGNC functional/gene-metadata prior ablation if the HGNC source prepares successfully.
- Any metric comparison is preliminary and specific to Kang PBMC IFN-beta and the project-defined held-out cell-type suite.

Forbidden:

- real evolutionary/conservation-prior benefit unless orthology/conservation features are present;
- SOTA or public benchmark claims;
- biological discovery;
- causal evolutionary explanation;
- neural EvoPrior or integrated model claims.
