# v0.11 External Public Benchmark Ingestion Plan

Status: v0.11 design document for manifest-driven public benchmark ingestion planning.

## Purpose

v0.11 adds scaffolding for external public benchmark ingestion. It is not a model
improvement milestone and does not create new model performance evidence.

The goal is to make future benchmark ingestion safe, provenance-tracked, and compatible
with the v0.10 benchmark evidence harness without committing raw data or downloading large
external artifacts in this round.

## Allowed Scope

v0.11 may:

- define a benchmark registry schema;
- define a dataset manifest schema;
- define a benchmark adapter interface;
- validate local metadata and small fixtures;
- validate local path existence without reading large matrices;
- generate an auditable ingestion plan;
- expose metadata-only records as blocked/not-run evidence candidates for v0.10.

## Forbidden Scope

v0.11 must not:

- download large datasets;
- commit raw data or derived output artifacts;
- train neural networks;
- add deep learning dependencies;
- tune hyperparameters on test labels;
- remove no-gene-prior or shuffled-prior negative controls;
- claim SOTA, public benchmark superiority, universal generalization, or true
  evolutionary/conservation-prior benefit.

## Required Provenance Fields

- `benchmark_id`
- `dataset_name`
- `source_type`
- `source_url_or_reference`
- `source_version_or_access_date`
- `license_or_terms`
- `citation`
- `organism`
- `modality`
- `perturbation_type`
- `cell_type_or_context`
- `split_policy`
- `leakage_risks`
- `local_path_status`
- `ingestion_status`
- `evidence_status`

## Ingestion Statuses

- `REGISTERED_METADATA_ONLY`
- `LOCAL_FIXTURE_VALIDATED`
- `LOCAL_DATA_READY`
- `INGESTED`
- `BLOCKED_MISSING_DATA`
- `BLOCKED_LICENSE_OR_TERMS`
- `BLOCKED_SCHEMA_MISMATCH`

## Evidence Statuses

- `NOT_RUN`
- `SMOKE_ONLY`
- `SAME_SPLIT_COMPARABLE`
- `CROSS_DATASET_COMPARABLE`
- `BLOCKED`

## Claim Rule

Metadata registration is not benchmark evidence.
Successful ingestion is not performance evidence.
Performance evidence requires a model run plus a v0.10 benchmark evidence record.

## Expected Outputs

The v0.11 planning runner writes:

- `public_benchmark_ingestion_plan.json`
- `public_benchmark_ingestion_table.csv`
- `public_benchmark_ingestion_report.md`
- `run_manifest.json`
- `resolved_config.yaml`

## Rollback

Rollback point: `v0.10-public-benchmark-alignment`.
