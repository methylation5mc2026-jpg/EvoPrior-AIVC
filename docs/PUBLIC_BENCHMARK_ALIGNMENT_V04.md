# Public Benchmark Alignment Audit v0.4

Status: current v0.4 setup is **not aligned** with a public leaderboard or paper benchmark split.

## Summary

The selected v0.4 dataset, `scperturb_papalexi_2021_arrayed_rna`, is suitable for real-data plumbing and baseline hardening. It is not currently configured as a benchmark-comparable setup against GEARS, CPA, scGen, Systema, Virtual Cell Challenge, or CZI Virtual Cells Platform results.

Therefore, v0.4 results must be described as project-defined engineering baselines, not public benchmark performance.

## Alignment Table

| Benchmark/source | Dataset | Perturbation type | Split | Metric | Preprocessing | Reproducibility status | Relation to current v0.4 | Action required |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GEARS | Norman et al. Perturb-seq, Adamson, Replogle subsets | genetic perturbation | GEARS-defined train/test generalization classes | perturbation prediction metrics from GEARS | GEARS/cell-gears processing | public code and paper exist | not aligned; current dataset is Papalexi arrayed RNA | add a GEARS-compatible dataset/config and reproduce split |
| CZI Virtual Cells Platform Adamson | Adamson unfolded protein response Perturb-seq | genetic perturbation | published train/val/test split; page reports 57/7/22 perturbation split | platform-specific benchmark metrics | log-normalized, top 5000 HVGs per platform page | public platform page exists | not aligned; current dataset and split differ | add Adamson config and platform split |
| CZI / NVIDIA K562 Essential | Replogle K562 essential Perturb-seq | CRISPRi genetic perturbation | platform benchmark split | platform-specific benchmark metrics | platform-defined | public platform page exists | not aligned; current file is Papalexi | add K562 essential adapter/config |
| scPerturb | 44 harmonized perturbation datasets | mixed CRISPR/drug/protein/ATAC | resource does not impose one universal prediction split | E-statistics and perturbation effect analysis | harmonized H5AD files | public data resource exists | partially related only by data source | define or find a prediction split for selected dataset |
| Systema / recent perturbation benchmarks | Adamson/Replogle/other standardized genetic perturbation tasks | genetic perturbation | standardized unseen perturbation tasks | simple baseline vs model comparisons | paper-specific | paper exists; exact assets need follow-up | not aligned | inspect released code/data and add compatible config |
| scGen examples | perturbation/cell-type response examples | stimulation / perturbation response | task-specific heldout cell type/context | latent response prediction metrics | scGen-specific | not aligned | not aligned | only compare after matching data and split |

## Current v0.4 Setup

- Dataset: `PapalexiSatija2021_eccite_arrayed_RNA.h5ad`.
- Source: scPerturb Zenodo v1.4.
- Split 1: repeated random-group split.
- Split 2: leave-one-perturbation suite over perturbations with at least two guide-level groups.
- Metrics: delta MAE/MSE/correlation, retrieval metrics, DE recovery metrics, confidence intervals.
- Preprocessing: active H5AD `X`, gene expression cell filter, top variance gene selection, guide-level pseudobulk.

This setup is useful for engineering discipline, but it is not a public benchmark.

## What Would Be Required To Claim Alignment

To claim alignment with a public benchmark, the project must document:

1. exact dataset file and checksum,
2. exact preprocessing pipeline,
3. exact gene set,
4. exact train/val/test split,
5. exact metric implementation,
6. baseline and model configs,
7. seed policy and repeated runs,
8. evidence that published and local split definitions match.

## Recommended Next Benchmark Target

For v0.5/v0.6 planning, do not immediately jump to novelty on this Papalexi split. A stronger benchmark-aligned path is:

1. Adamson UPR Perturb-seq from CZI Virtual Cells Platform or GEARS/cell-gears.
2. Norman 2019 filtered perturb-seq for GEARS-compatible perturbation generalization.
3. Replogle K562 essential for a standard single-cell genetic perturbation prediction benchmark.
4. Parse PBMC cytokine only after storage/runtime constraints and official split access are clear.

## Sources Checked

- scPerturb Zenodo: <https://zenodo.org/records/13350497>
- scPerturb project: <https://projects.sanderlab.org/scperturb/>
- Papalexi pertpy note: <https://pertpy.readthedocs.io/en/1.0.6/api/data/pertpy.data.papalexi_2021.html>
- GEARS paper: <https://www.nature.com/articles/s41587-023-01905-6>
- CZI Adamson page: <https://virtualcellmodels.cziscience.com/dataset/adamson-human-tcells>
- CZI K562 Essential page: <https://virtualcellmodels.cziscience.com/dataset/k562-essential-perturb-seq>
- Systema paper: <https://www.nature.com/articles/s41587-025-02777-8>
- Open Problems perturbation prediction overview: <https://openproblems.bio/results/perturbation_prediction>

