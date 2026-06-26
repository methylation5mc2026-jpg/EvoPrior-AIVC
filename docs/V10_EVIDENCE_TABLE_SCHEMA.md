# v0.10 Evidence Table Schema

Status: schema contract for benchmark evidence records.

## Record Identity

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `record_id` | string | yes | Stable local identifier derived from dataset, split, model, and run. |
| `run_dir` | string | yes | Source run directory. |
| `dataset_id` | string | yes | Dataset from manifest/config/path fallback. |
| `split_id` | string | yes | Split mode, split label, or configured suite. |
| `model_id` | string | yes | Baseline/model name. |
| `config_path` | string | no | Config path if recoverable. |

## Evidence Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `metrics` | object | no | Mean metric values or row-level metric summary. |
| `metrics_finite` | bool | yes | False if any numeric metric is NaN or infinite. |
| `coverage_manifest` | object | no | Gene-prior coverage or preparation metadata. |
| `component_audit` | object | no | Component audit summary when available. |
| `leakage_checks` | object | no | Split/leakage status when available. |
| `claim_boundary` | string | yes | Defaults to a conservative no-strong-claim boundary. |
| `evidence_status` | string | yes | `pass`, `weak`, `missing`, `invalid`, or `blocked`. |
| `missing_artifacts` | list[string] | yes | Files or evidence classes not present in the run. |
| `warnings` | list[string] | yes | Non-fatal issues. |

## Comparison Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `same_split_group` | string | no | Dataset/split key used for within-split comparison. |
| `lineage_comparison_status` | string | no | Whether a model can be compared with `lineage_shrinkage`. |
| `gene_prior_comparison_status` | string | no | Whether HGNC prior beats, matches, or trails no-gene-prior. |
| `shuffled_control_status` | string | no | Whether shuffled prior is present and comparable. |

## Status Rules

- `pass`: run exists, finite metrics exist, and no blocking artifact is missing.
- `weak`: run exists but evidence is insufficient for a stronger claim.
- `missing`: expected artifact is absent, but the run can still be cataloged.
- `invalid`: numeric metrics are not finite or a required identity field is not recoverable.
- `blocked`: evidence depends on unavailable external benchmark data or split definitions.

## Required Conservative Default

If `claim_boundary` cannot be found, collectors must use:

```text
No strong claim is supported by this record without manual review.
```

## Non-Goals

The schema does not store raw expression matrices, test labels, model checkpoints, raw data,
or generated `outputs/` artifacts in git.
