# v0.12 Benchmark Unblock Log

## Initial State

- Rollback point: `v0.11-external-public-benchmark-ingestion`
- v0.11 registered records: Kang metadata-only and Papalexi/scPerturb metadata-only.
- Local raw files observed:
  - `data/raw/kang_2018_pbmc_ifnb.h5ad`
  - `data/raw/PapalexiSatija2021_eccite_arrayed_RNA.h5ad`

## Decision

Papalexi/Satija scPerturb data is unblocked for v0.12 execution because the local H5AD exists, the configured checksum is locked, the file is below 2 GB, and the existing adapter/baseline layer supports it.

## Alignment Status

- Data source: public scPerturb-compatible H5AD.
- Split: custom leave-one-perturbation suite over guide-level pseudobulk groups.
- Metrics: internal compatible metrics.
- Official benchmark status: not official leaderboard aligned.

## Remaining Blockers

- Official GEARS/Norman data and split files are not locally registered.
- Public leaderboard comparability remains blocked until exact official split and metric scripts are imported.
- No raw data, outputs, or cache files should be committed.

## Execution Result

- Dry-run command passed: `python scripts/prepare_public_benchmark.py --config configs/data/public_benchmark_v012.yaml --dry-run`
- Prepare command passed: `python scripts/prepare_public_benchmark.py --config configs/data/public_benchmark_v012.yaml`
- Baseline command passed: `python scripts/run_public_benchmark_baseline.py --config configs/experiment/public_benchmark_v012_baseline.yaml`
- Output directory: `outputs/runs/v0.12-public-benchmark-baseline-run/scperturb_papalexi_2021_arrayed_rna_v012/20260624T150442Z/`
- Checksum status: `ok`
- Split leakage audit: passed
- Remaining blocker for stronger external claim: official split and official metric alignment are not imported.
