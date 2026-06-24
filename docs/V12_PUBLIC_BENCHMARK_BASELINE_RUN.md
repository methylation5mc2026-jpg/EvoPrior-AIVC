# v0.12 Public Benchmark Baseline Run

Status: completed for v0.12.

## Selection Table

| benchmark_id | source | official or compatible? | dataset | required files | access method | current blocker | unblock action | expected local size | expected runtime | expected split | metrics | decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `scperturb_papalexi_2021_arrayed_rna_v012` | scPerturb Zenodo record 13350497 | custom benchmark-compatible; not official leaderboard aligned | Papalexi/Satija 2021 ECCITE-seq RNA | `PapalexiSatija2021_eccite_arrayed_RNA.h5ad` | local file or legal public download | official split not imported | run custom leave-one-perturbation suite with explicit claim boundary | 52,339,395 bytes | minutes on CPU | leave-one-perturbation over guide-level pseudobulk groups | MAE, MSE, Pearson delta, Spearman logFC, DE top-k | run now |
| `kang_2018_pbmc_ifnb_metadata_only` | project-local Kang 2018 PBMC IFN-beta config | project-defined, not main v0.12 public benchmark | Kang 2018 PBMC IFN-beta | local H5AD | local file | not a perturbation prediction public benchmark target for v0.12 | keep as backward compatibility only | 38,356,412 bytes | minutes on CPU | held-out cell type | existing metrics | defer |
| GEARS/Norman official-style | GEARS/Norman community benchmark | preferred if official split/data are available | Norman combinatorial Perturb-seq | official data and split files | network/manual | not registered locally in v0.11 and no local files are present | defer until legal local data/split are obtained | unknown until source is locked | unknown | official or GEARS-compatible combo split | GEARS-compatible metrics | defer |

## Selected Benchmark

`scperturb_papalexi_2021_arrayed_rna_v012` is selected because the public H5AD is already present locally with a locked md5 and can be executed today without a large uncontrolled download.

## Claim Boundary

This milestone may claim a reproducible public-data, benchmark-compatible baseline run under a custom split. It must not claim official leaderboard alignment, SOTA, biological discovery, or general EvoPrior superiority.

## Completed Run

- Command: `python scripts/run_public_benchmark_baseline.py --config configs/experiment/public_benchmark_v012_baseline.yaml`
- Output directory: `outputs/runs/v0.12-public-benchmark-baseline-run/scperturb_papalexi_2021_arrayed_rna_v012/20260624T150442Z/`
- Data report directory: `outputs/data_reports/scperturb_papalexi_2021_arrayed_rna_v012/20260624T150442Z/`
- Data checksum status: `ok`
- Split leakage audit: passed
- Official alignment: custom benchmark-compatible, not official leaderboard aligned
- Test held-out perturbations: `etv7`, `pdl1`
- Test metrics are underpowered: `n=2`

## Main Metric Snapshot

| split | baseline | MAE | MSE | Pearson delta | Spearman logFC | DE top-20 precision |
| --- | --- | --- | --- | --- | --- | --- |
| test | `no_change` | 0.2388 | 1.7221 | unavailable | unavailable | 0.0000 |
| test | `control_mean` | 0.2388 | 1.7221 | unavailable | unavailable | 0.0000 |
| test | `mean_delta` | 0.6922 | 5.7392 | 0.5692 | 0.3210 | 0.5125 |
| test | `perturbation_mean_delta_v2` | 0.6922 | 5.7392 | 0.5692 | 0.3210 | 0.5125 |
| test | `hierarchical_additive` | 0.6922 | 5.7392 | 0.5692 | 0.3210 | 0.5125 |
| test | `ridge_cv` | 0.7152 | 6.0478 | 0.5656 | 0.3181 | 0.5125 |
| test | `evoprior_additive_no_prior` | 0.6922 | 5.7392 | 0.5692 | 0.3210 | 0.5125 |

Interpretation: this is a reproducibility and benchmark-compatibility milestone. The low n and custom split prevent strong performance claims.

## Required Commands

```powershell
python scripts/prepare_public_benchmark.py --config configs/data/public_benchmark_v012.yaml --dry-run
python scripts/prepare_public_benchmark.py --config configs/data/public_benchmark_v012.yaml
python scripts/run_public_benchmark_baseline.py --config configs/experiment/public_benchmark_v012_baseline.yaml
```
