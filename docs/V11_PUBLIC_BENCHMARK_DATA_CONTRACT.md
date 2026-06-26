# v0.11 Public Benchmark Data Contract

Status: data contract for metadata-first public benchmark registration.

## Registry Record

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `benchmark_id` | string | yes | Normalized lower-case identifier. |
| `dataset_name` | string | yes | Human-readable dataset or benchmark name. |
| `source_type` | string | yes | Example: `paper`, `repository`, `zenodo`, `figshare`, `local_fixture`. |
| `source_url_or_reference` | string | yes | URL, DOI, accession, or textual reference. |
| `source_version_or_access_date` | string | yes | Version, release, or access date. |
| `license_or_terms` | string | yes | License or data-use terms. |
| `citation` | string | yes | Citation text or DOI. |
| `organism` | string | yes | Species or organism group. |
| `modality` | string | yes | Example: `scRNA-seq`, `Perturb-seq`, `pseudobulk`. |
| `perturbation_type` | string | yes | Example: `drug`, `CRISPR`, `cytokine`, `stimulus`. |
| `cell_type_or_context` | string | yes | Cell type, tissue, organism context, or mixed. |
| `split_policy` | string | yes | Official, project-defined, unavailable, or planned split policy. |
| `leakage_risks` | list[string] | yes | Known leakage or comparability risks. |
| `local_path_status` | string | yes | `missing`, `fixture`, `ready`, or `not_applicable`. |
| `ingestion_status` | string | yes | One of the v0.11 ingestion statuses. |
| `evidence_status` | string | yes | One of the v0.11 evidence statuses. |

Optional fields:

- `local_paths`
- `expected_files`
- `optional_files`
- `expected_columns`
- `adapter`
- `notes`

## Local Path Rules

- Metadata-only records do not require local paths.
- `LOCAL_DATA_READY` and `INGESTED` records require all declared required local paths
  to exist.
- Paths under `outputs/`, cache folders, and `egg-info` are unsafe for input data and must
  fail validation.
- The validator checks path existence but must not read large expression matrices.

## Adapter Contract

An adapter must expose:

- `benchmark_id`
- `validate_metadata()`
- `validate_local_files()`
- `describe_expected_inputs()`
- `build_ingestion_plan()`

The ingestion plan must include:

- required files;
- optional files;
- expected columns or keys;
- split policy;
- leakage risks;
- blocked reasons;
- whether model training or performance claims were produced.

## Evidence Compatibility

Registry records may become v0.10-compatible evidence candidates with status `blocked` or
`missing`, but they must not be converted into model performance evidence until a model run
and benchmark evidence record exist.
