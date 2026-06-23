# 基准评测

状态：初始设计稿。正式模型比较前必须锁定 split、metric、配置和评测脚本版本。

## 最小 v0.1 benchmark

第一阶段只做最小可信基线：

- no-change baseline。
- train mean baseline。
- additive perturbation/cell-type baseline。
- ridge/linear baseline。

所有基线必须在同一 preprocessing、同一 gene set、同一 split、同一评测脚本下运行。

## 初始 split 类型

| Split ID | 目的 | 训练/测试约束 |
| --- | --- | --- |
| `heldout_perturbation` | 测试未见扰动外推 | 测试扰动不允许出现在训练/验证中 |
| `heldout_cell_type` | 测试未见细胞类型外推 | 测试细胞类型不允许出现在训练/验证中 |
| `heldout_donor` | 测试 donor 泛化 | 测试 donor 不允许出现在训练/验证中 |
| `heldout_context` | 测试组合上下文外推 | 明确定义 cell_type/donor/perturbation 组合，避免隐式泄漏 |

## 初始 metrics

- MAE。
- MSE。
- Pearson delta correlation。
- Spearman log-fold-change correlation。
- top-k DE overlap precision。
- 后续：perturbation discrimination score。
- 后续：per-cell-type、per-perturbation、per-donor breakdown。

## 锁定评测要求

正式比较前必须满足：

- `src/evoprior_aivc/evaluation/metrics.py` 的指标定义有合成案例测试。
- `src/evoprior_aivc/data/splits.py` 的切分逻辑有泄漏测试。
- 每个实验保存 config、seed、git commit、dataset checksum、split ID、metrics JSON、prediction file、log file。
- `docs/CLAIMS_AND_EVIDENCE.md` 只引用有 experiment ID 的结果。

## 不允许的声称

- 不允许凭单次 seed 声称 SOTA。
- 不允许不同 preprocessing 或不同 split 之间直接比较。
- 不允许把 validation 调参结果当作 held-out test 结果。
- 不允许把未跑过的公开模型写成“已超过”。

## v0.2 synthetic baseline smoke benchmark

Experiment ID: `v0.2-synthetic-baseline-smoke`

目的：验证工程 substrate，而不是验证生物学假设。

命令：

```powershell
python scripts/run_baseline.py --config configs/experiment/synthetic_v02.yaml
```

数据：`make_synthetic_perturbation_adata()` 生成的 deterministic synthetic AnnData。

聚合：按 `cell_type`、`perturbation`、`donor` 做 pseudobulk mean aggregation。

预测目标：先预测 delta expression，再用 matched control expression 重构 predicted post expression。

baseline：

- `no_change`: delta = 0。
- `mean_delta`: seen perturbation 使用训练平均 delta，unseen perturbation 使用 global mean fallback。
- `additive`: global mean delta + perturbation offset + cell-type offset。
- `ridge`: control expression + perturbation/cell_type/donor one-hot，目标为 delta expression。

split：

- `random_group`: pseudobulk non-control group 随机切分。
- `heldout_perturbation`: `pert_c` 只在 test 中出现，用于测试 unseen perturbation fallback 是否无泄漏。

指标：

- `mae_delta`
- `mse_delta`
- `pearson_delta`
- `spearman_logfc`
- per-cell-type 和 per-perturbation breakdown CSV。

解释边界：synthetic benchmark 只能证明 runner、artifact discipline、baseline API 和 metrics plumbing 能跑通。即使某个 baseline 在 synthetic split 上表现好，也不能说明其对真实生物数据有效。

## v0.3 real benchmark baseline smoke

Experiment ID: `v0.3-real-benchmark-baselines`

Dataset ID: `scperturb_papalexi_2021_arrayed_rna`

Command:

```powershell
python scripts/run_real_baseline.py --config configs/experiment/real_v03_baselines.yaml
```

Output pattern:

```text
outputs/runs/v0.3-real-benchmark-baselines/scperturb_papalexi_2021_arrayed_rna/<timestamp>/
```

Data preparation:

```powershell
python scripts/prepare_dataset.py --config configs/data/real_v03.yaml --dry-run
python scripts/prepare_dataset.py --config configs/data/real_v03.yaml
```

Schema mapping:

- `perturbation` -> `perturbation`
- `celltype` -> `cell_type`
- `tissue_type` -> `tissue`
- inferred control mask from `control`
- `var_names` -> `gene_symbol`
- `ensembl_id` -> `gene_id`

Pseudobulk:

- Grouping: `cell_type`, `perturbation`, `guide_id`
- Minimum cells per group: 20
- Aggregation: mean
- Matched control: pooled by `cell_type`

Splits:

- `random_group`: group-level engineering sanity split.
- `heldout_perturbation`: `pdl1` held out from train/val and evaluated as unseen perturbation.

Baselines:

- no-change
- mean-delta
- additive
- ridge

Metrics:

- `mae_delta`
- `mse_delta`
- `pearson_delta`
- `spearman_logfc`
- per-perturbation and per-cell-type breakdowns
- top failure cases by group-level MAE

What this tests:

- The project can ingest one real public H5AD perturbation dataset.
- Canonical schema validation works on messy real metadata.
- Pseudobulk grouping, split, leakage checks, baselines, metrics, and artifact saving run end-to-end.

What this does not test:

- SOTA or near-SOTA performance.
- Lineage, donor, or tissue generalization.
- EvoPrior or evolutionary priors.
- Agreement with a published benchmark split.

## v0.4 strengthened real-data baseline evaluation

Experiment ID: `v0.4-real-baseline-strengthening`

Command:

```powershell
python scripts/run_repeated_baselines.py --config configs/experiment/real_v04_repeated_baselines.yaml
```

Output pattern:

```text
outputs/runs/v0.4-real-baseline-strengthening/scperturb_papalexi_2021_arrayed_rna/<timestamp>/
```

New baselines:

- `control_mean`: explicit matched-control zero-delta baseline with fallback hierarchy documented.
- `perturbation_mean_delta_v2`: perturbation mean delta with guide/global/zero fallback options.
- `hierarchical_additive`: global + perturbation + guide + cell-type + batch effects with shrinkage.
- `ridge_cv`: ridge baseline with alpha selected from a fixed grid.

Repeated split modes:

- `repeated_random_group`: 5 group-level random splits by default.
- `leave_one_perturbation_suite`: holds out each perturbation with at least two pseudobulk groups; skipped perturbations are reported.

Confidence intervals:

- v0.4 reports mean, standard deviation, and normal-approximation 95% CI.
- `underpowered=True` is reported when fewer than 3 values support the interval.
- For the current dataset, leave-one perturbation CI values are underpowered.

Perturbation retrieval / PDS:

- Candidate perturbation profiles are built from training observed deltas only.
- If the true held-out perturbation is absent from train candidates, retrieval is marked not meaningful.
- This conservative design avoids using test target profiles as candidate references.

DE recovery:

- Reports top-k absolute delta overlap precision, Jaccard, signed direction accuracy, and gene-rank Spearman.
- Configured k values: 20, 50, 100.
- Metrics are engineering checks over selected genes, not biological discovery claims.

Preprocessing sensitivity:

Command:

```powershell
python scripts/run_sensitivity.py --config configs/experiment/real_v04_sensitivity.yaml
```

Audited dimensions:

- top variance genes: 1000, 3000, 5000
- min cells per pseudobulk group: 10, 20, 50
- split modes: random_group, heldout_pdl1

Benchmark alignment:

- Current Papalexi/scPerturb v0.4 split is not aligned with GEARS, CPA, scGen, Systema, Virtual Cell Challenge, or CZI platform splits.
- See `docs/PUBLIC_BENCHMARK_ALIGNMENT_V04.md`.
