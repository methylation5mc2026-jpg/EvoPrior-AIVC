# v0.8 Real Gene Prior Coverage Report

Status: durable summary of the v0.8 Kang HGNC metadata-prior coverage check.

Run-specific report:

```text
outputs/data_reports/kang_2018_pbmc_ifnb/20260624T010126Z/real_gene_prior_v08_coverage_report.md
```

Prepared source:

- mode: `download_hgnc`
- kind: `real_functional_gene_metadata`
- source URL: `https://storage.googleapis.com/public-download-files/hgnc/tsv/tsv/hgnc_complete_set.txt`
- source version note: `hgnc_complete_set_current_page_date_2026-06-19`
- source md5: `a49771d2d247b54ec606007ed733ae64`
- feature table md5: `a4ec5c04c9a597cd548031e89f0d75d1`

Feature columns:

- `hgnc_gene_group_count`
- `is_immune_related`
- `approved_symbol_present`
- `gene_biotype`
- `locus_group`

Coverage over the evaluated Kang v0.8 gene set:

- total genes: 2,000
- mapped genes: 1,875
- missing genes: 125
- coverage fraction: 0.9375

Decision:

Real HGNC metadata-prior ablation is allowed. This does not test real evolutionary/conservation-prior benefit because no orthology, conservation score, or gene-age source is configured.
