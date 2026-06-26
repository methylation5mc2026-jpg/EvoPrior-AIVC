# v0.23 Project Page Assets

## Project Title

EvoPrior-AIVC

## One-Sentence Summary

Reproducible single-cell perturbation-response benchmark pipeline with structured priors and a validated residual baseline on a GEARS-compatible Norman/scPerturb split.

## 150-Word Project Description

EvoPrior-AIVC is a research engineering project for single-cell perturbation-response prediction. It builds a reproducible pipeline around public perturbation datasets, schema validation, leakage-aware splits, transparent baselines, structured priors, and release-ready evidence tracking. The strongest packaged result is a PCA/Ridge residual correction model evaluated on the Norman/scPerturb combinatorial perturbation dataset under a fixed internal GEARS-compatible split. Across five seeds, the validated residual baseline reports MAE `0.430778`, MSE `3.668870`, Pearson delta `0.869224`, and Spearman logFC `0.784976`, with critical leakage stress checks passed. The project is intentionally conservative: it does not claim official GEARS, leaderboard comparability, SOTA, or biological discovery. Instead, it emphasizes reproducible methodology, honest claim boundaries, public data provenance, and a review package that a computational biology mentor can inspect quickly.

## 300-Word Project Description

EvoPrior-AIVC is a reproducible benchmark and evidence package for single-cell perturbation-response prediction. The project started from synthetic sanity checks and grew into a staged research pipeline covering public H5AD ingestion, canonical schema mapping, pseudobulk construction, leakage-aware splits, baseline comparison, lineage/gene-prior experiments, public benchmark planning, Norman/scPerturb benchmarking, release smoke tests, and public GitHub packaging.

The current public-facing result centers on the Norman/scPerturb combinatorial perturbation dataset, file `NormanWeissman2019_filtered.h5ad`, md5 `c870e6967d91c017d9da827bab183cd6`. The benchmark uses a fixed internal GEARS-compatible seen0/seen1/seen2/random_combo split. The primary model is a PCA/Ridge residual correction over a weighted combo additive baseline. On the locked v0.17 evaluation, the model reports five-seed aggregate metrics of MAE `0.430778`, MSE `3.668870`, Pearson delta `0.869224`, and Spearman logFC `0.784976`. Leakage stress checks passed, and the release package includes a model card, benchmark card, runbook, result card, public demo guide, artifact manifest, and mentor review brief.

The project is designed to be credible rather than inflated. It explicitly does not claim official GEARS, leaderboard comparability, SOTA, clinical use, biological discovery, or broad superiority. That boundary is part of the contribution: the repository shows how to package an AI-biology benchmark result with provenance, splits, commands, checksums, and failure modes intact.

## Technical Highlights

- Public H5AD data ingestion with checksum tracking.
- Canonical schema mapping and pseudobulk construction.
- Leakage-aware split and stress checks.
- Transparent additive, neural-style, and residual baselines.
- Five-seed validation of the selected residual baseline.
- No-data review path for GitHub readers.
- With-data reproduction path for reviewers with local Norman data.
- Public release notes, model card, benchmark card, and runbook.

## Benchmark Result Table

| model | seeds | MAE | MSE | Pearson delta | Spearman logFC |
| --- | ---: | ---: | ---: | ---: | ---: |
| v0.14 weighted combo additive | 1 | 0.5660 | 6.6759 | 0.7599 | 0.6390 |
| v0.15 fast MLP/PCA | 3 | 0.5877 | 7.5517 | 0.7134 | 0.6317 |
| v0.17 validated residual baseline | 5 | 0.430778 | 3.668870 | 0.869224 | 0.784976 |

## What I Built

- A staged Python research repo for perturbation-response prediction.
- Dataset preparation, schema validation, and split documentation.
- A GEARS-compatible Norman benchmark package with a locked internal split.
- A residual correction baseline with model cards and leakage audits.
- A public review package suitable for GitHub, mentors, and personal website presentation.

## Why It Matters

AI-biology results are easy to overstate when datasets, splits, and metrics are loosely defined. EvoPrior-AIVC focuses on the engineering discipline around a result: exact data checksum, fixed split status, reproducible commands, audit trails, and explicit claim boundaries. This makes the project useful for learning, review, and future benchmark strengthening.

## Limitations And Honesty

- The Norman split is GEARS-compatible/internal, not official GEARS.
- The result is not leaderboard-comparable.
- The project does not claim SOTA or biological discovery.
- Official GEARS execution remains blocked.
- Raw data is not committed; reviewers must obtain it legally and verify the checksum.

## Suggested Project Card

- Title: EvoPrior-AIVC
- Subtitle: Reproducible perturbation-response benchmarking with a validated Norman residual baseline.
- Tags: single-cell, Perturb-seq, computational biology, reproducibility, Norman, GEARS-compatible
- Metrics: MAE 0.430778, MSE 3.668870, Pearson 0.869224, Spearman 0.784976
- GitHub link: `<YOUR_GITHUB_REPO_URL>`

## Suggested Figure Descriptions

- Pipeline diagram: raw Norman/scPerturb H5AD to schema mapping, split, additive baseline, residual PCA/Ridge correction, evaluation, and release package.
- Benchmark result table: v0.14 weighted additive, v0.15 fast MLP/PCA, and v0.17 validated residual baseline.
- Residual correction idea: combo response equals additive effect plus low-rank residual correction learned from training perturbations.

## Short Chinese Explanation

EvoPrior-AIVC 是一个单细胞扰动响应预测项目，重点不是夸大模型效果，而是把公开数据、固定切分、基线模型、泄漏检查、复现命令和声明边界完整打包。当前最强结果是在 Norman/scPerturb 数据的 GEARS-compatible 内部切分上，PCA/Ridge residual baseline 相比已有内部基线更强；但它不是官方 GEARS、不是排行榜结果，也不声称 SOTA。
