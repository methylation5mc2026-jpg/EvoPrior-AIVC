# v0.24 Website Integration Assets

## Project Title

EvoPrior-AIVC: Reproducible Perturbation Prediction Benchmarking

## One-Line Summary

A public-review-ready research repository for single-cell perturbation-response prediction, with auditable data provenance, split discipline, and a validated internal GEARS-compatible Norman residual baseline.

## Short Card

EvoPrior-AIVC is a reproducible Python research package for single-cell perturbation-response prediction. The current public review package centers on a validated residual baseline on a public Norman/scPerturb dataset using a documented internal GEARS-compatible split. Claims are intentionally narrow: the result is not official GEARS, not leaderboard-comparable, and not SOTA.

## 150-Word Summary

EvoPrior-AIVC explores evidence-disciplined perturbation prediction for single-cell biology. The project started from synthetic and real-data baseline plumbing, then added lineage-prior and gene-prior modules, public benchmark ingestion, Norman/scPerturb GEARS-compatible evaluation, residual baseline validation, release packaging, and public presentation assets. The strongest current result is a project-owned residual baseline on a public Norman/scPerturb H5AD with md5 `c870e6967d91c017d9da827bab183cd6`, evaluated on a fixed internal GEARS-compatible seen0/seen1/seen2/random_combo split. Five documented seeds produced mean MAE 0.430778, MSE 3.668870, Pearson delta 0.869224, and Spearman logFC 0.784976. The repository emphasizes reproducibility, leakage audits, claim boundaries, release smoke checks, and public-review documentation. It does not claim official GEARS alignment, leaderboard comparability, SOTA, biological discovery, clinical utility, or general model superiority.

## Result Table

| Model | MAE | MSE | Pearson | Spearman | Status |
| --- | ---: | ---: | ---: | ---: | --- |
| weighted combo additive | 0.5660 | 6.6759 | 0.7599 | 0.6390 | transparent baseline |
| fast MLP/PCA | 0.5877 | 7.5517 | 0.7134 | 0.6317 | lightweight trained baseline |
| residual baseline | 0.430778 | 3.668870 | 0.869224 | 0.784976 | five-seed validated internal result |

## Suggested Page Sections

- Problem: perturbation response prediction needs reproducible evidence and careful claim boundaries.
- Approach: baseline-first pipeline, public data provenance, split manifests, leakage audits, and release smoke checks.
- Current result: validated residual baseline under one fixed internal Norman split.
- What is honest: strong internal GEARS-compatible result.
- What is not claimed: official GEARS, leaderboard, SOTA, biology discovery, or clinical use.
- Links: README, model card, benchmark card, reproducibility runbook, release notes, publish guide.

## Chinese Summary

EvoPrior-AIVC 是一个面向单细胞扰动响应预测的可复现实验仓库。当前最强证据来自公开 Norman/scPerturb 数据上的内部 GEARS-compatible split 和五种子 residual baseline 验证。这个结果适合展示工程严谨性、数据溯源、split/metric 锁定、泄漏审计和诚实的科学边界；它不能被描述为官方 GEARS、排行榜结果、SOTA、临床结论或生物学发现。
