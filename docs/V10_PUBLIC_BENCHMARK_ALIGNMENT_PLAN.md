# v0.10 Public Benchmark Alignment Plan

Status: v0.10 design document for benchmark alignment and evidence hardening.

## Goal

v0.10 aligns existing v0.6-v0.9 benchmark outputs into one reproducible evidence layer.
It does not add model capacity, train neural models, import external benchmark data, tune on
test metrics, or create stronger biological claims.

## Evaluation Objects

- `lineage_shrinkage`: v0.6 Kang lineage benchmark.
- `gene_prior`: v0.7 synthetic/Kang compatibility and v0.8 HGNC metadata-prior runs.
- `EvoPriorAdditive`: v0.9 integrated additive runs.
- `no_gene_prior`: negative control for additive gene-prior attribution.
- `shuffled_prior`: negative control when present in a run.

## Evidence Inputs

Each evidence record is collected from a run directory and may include:

- `metrics.csv` and `metric_summary.csv`
- `report.md`
- `run_manifest.json`
- `resolved_config.yaml`
- `gene_prior_preparation.json`
- `component_audit.md`
- `component_audit_summary.json`
- coverage reports or coverage fields in manifests
- split manifests and leakage-check artifacts when present

Missing files are not fatal. They must be recorded as `missing` rather than silently ignored.

## Unified Fields

- `dataset_id`
- `split_id`
- `model_id`
- `config_path`
- `run_dir`
- `metrics`
- `coverage_manifest`
- `component_audit`
- `leakage_checks`
- `claim_boundary`
- `evidence_status`

## Claim Ladder

- PASS: reproducible benchmark run exists.
- PASS: numeric metrics are finite.
- PASS: compared models use the same dataset and split.
- PASS: component audit is available when a component claim is being discussed.
- WEAK: HGNC gene-prior benefit is not established when HGNC underperforms or only matches
  the no-gene-prior negative control.
- BLOCKED: public external benchmark alignment is not established until external benchmark
  data, split definitions, and adapters are explicitly imported and versioned.

## Explicit Non-Claims

v0.10 does not prove:

- SOTA or public leaderboard performance;
- true evolutionary/conservation-prior benefit;
- cross-dataset generalization;
- neural model effectiveness;
- biological discovery.

## Deliverables

- `src/evoprior_aivc/evaluation/benchmark_evidence.py`
- `scripts/run_benchmark_alignment.py`
- `configs/experiment/v10_benchmark_alignment_synthetic.yaml`
- `configs/experiment/v10_benchmark_alignment_kang.yaml`
- `benchmark_evidence.json`
- `benchmark_evidence_table.csv`
- `benchmark_evidence_report.md`

## Rollback

Rollback point: `v0.9-integrated-evoprior-additive-model`.
