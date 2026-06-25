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

## v0.5 synthetic lineage-prior sanity benchmark

Experiment ID: `v0.5-synthetic-lineage-prior`

Command:

```powershell
python scripts/run_lineage_prior.py --config configs/experiment/synthetic_v05_lineage.yaml
```

Output pattern:

```text
outputs/runs/v0.5-first-lineage-prior/synthetic_lineage/<timestamp>/
```

Data:

- Generated by `make_synthetic_lineage_adata()`.
- Eight synthetic cell types arranged under immune, epithelial, and stromal branches.
- Five non-control perturbations plus control.
- Two donors and two batches.
- Response generation includes global perturbation effect, lineage-shared effect, cell-type-specific effect, donor offset, and residual noise.

Split:

- `heldout_cell_type`: each configured target cell type is absent from train and evaluated only in test.
- Current config holds out representative sibling pairs across major branches.
- This split is designed to check whether related training cell types can be borrowed from without using target post-perturbation expression.

Baselines:

- `control_mean`
- `mean_delta`
- `perturbation_mean_delta_v2`
- `hierarchical_additive`
- `ridge_cv`
- `lineage_shrinkage`

Metrics:

- `mae_delta`
- `mse_delta`
- `pearson_delta`
- `spearman_logfc`
- DE recovery summary over top-k absolute delta genes.

What this tests:

- The lineage tree, mapping, lineage distance, and relatedness-kernel utilities are wired into a benchmark.
- A non-neural lineage-aware baseline can train only on non-held-out cell types and predict held-out cell types.
- Under a known synthetic lineage-structured generator, the expected borrowing behavior is measurable.

What this does not test:

- Real biological lineage benefit.
- Public leaderboard alignment.
- Neural EvoPrior, evolutionary priors, pathway priors, or SOTA performance.

## v0.5 Papalexi lineage compatibility check

Experiment ID: `v0.5-papalexi-lineage-compatibility`

Command:

```powershell
python scripts/run_lineage_prior.py --config configs/experiment/real_v05_lineage_compatibility.yaml
```

Output pattern:

```text
outputs/runs/v0.5-first-lineage-prior/scperturb_papalexi_2021_arrayed_rna/<timestamp>/
```

Purpose:

- Confirm that `LineageShrinkageBaseline` degrades safely on the existing real-data plumbing.
- Record that Papalexi has one configured cell type/cell line and cannot identify lineage signal.

Interpretation:

- Compatibility/no-op only.
- Metrics from this run are not evidence that lineage priors improve real biological prediction.

## v0.6 real multi-cell-type lineage benchmark

Experiment ID: `v0.6-real-multicell-lineage-benchmark`

Dataset ID: `kang_2018_pbmc_ifnb`

Command:

```powershell
python scripts/run_lineage_real_benchmark.py --config configs/experiment/real_v06_multicell_lineage.yaml
```

Output:

```text
outputs/runs/v0.6-real-multicell-lineage-benchmark/kang_2018_pbmc_ifnb/20260623T092131Z/
```

Data:

- Kang 2018 PBMC IFN-beta H5AD.
- 8 normalized PBMC cell types.
- `ctrl` and `stim` labels.
- donor-like `replicate` mapped to canonical `donor`.
- coarse hematopoietic lineage mapping in `configs/priors/lineage_real_multicell_v06.yaml`.

Split modes:

- `heldout_cell_type_suite`: hold out each eligible cell type's stimulated pseudobulks one at a time.
- `heldout_lineage_suite`: hold out coarse `lymphoid` or `myeloid` clades when feasible.

Control policy:

- `control_observed_ood`.
- Held-out cell-type controls may be used as input control state.
- Held-out cell-type stimulated deltas are test-only and absent from train/validation.

Baselines:

- `control_mean`
- `mean_delta`
- `perturbation_mean_delta_v2`
- `hierarchical_additive`
- `ridge_cv`
- `lineage_shrinkage`

Primary held-out cell-type result:

- `lineage_shrinkage` test MAE mean 0.3160 versus 0.4221 `control_mean`, 0.4317 `mean_delta`, 0.4317 `hierarchical_additive`, and 0.4969 `ridge_cv`.
- `lineage_shrinkage` test MSE mean 4.9515 versus 13.0753 `control_mean`, 9.7610 `mean_delta`, 9.7610 `hierarchical_additive`, and 8.8297 `ridge_cv`.
- `lineage_shrinkage` test Pearson mean 0.7399 versus 0.6685 `mean_delta` and 0.7190 `ridge_cv`.
- `lineage_shrinkage` test Spearman logFC mean 0.5887 versus 0.5608 `mean_delta` and 0.4070 `ridge_cv`.

DE recovery:

- In held-out cell-type suite, `lineage_shrinkage` has top-20 precision 0.6295 and top-50 precision 0.6546.
- This is higher than `mean_delta` / `hierarchical_additive` top-20 precision 0.5795 and top-50 precision 0.6321 in this run.

Underpowered warnings:

- Held-out cell-type suite has n=7 eligible cell types and is the primary result.
- Held-out lineage suite has n=2 clades and is underpowered; do not draw strong clade-level conclusions.
- `megakaryocytes` is skipped in held-out cell-type suite because it has too few test groups.

What this tests:

- Real multi-cell-type PBMC IFN-beta held-out cell-type transfer under a documented control policy.
- Whether the v0.5 non-neural lineage shrinkage baseline helps on this one dataset/split.

What this does not test:

- General lineage-prior superiority.
- Multiple perturbation identity transfer.
- Public leaderboard alignment.
- Neural EvoPrior, evolutionary prior, or pathway prior.

## v0.6 tau sensitivity audit

Experiment ID: `v0.6-real-multicell-lineage-tau-audit`

Command:

```powershell
python scripts/run_lineage_real_benchmark.py --config configs/experiment/real_v06_lineage_tau_audit.yaml
```

Output:

```text
outputs/runs/v0.6-real-multicell-lineage-tau-audit/kang_2018_pbmc_ifnb/20260623T092131Z/
```

Pre-specified tau values: 0.5, 1.0, 2.0, 4.0.

Held-out cell-type MAE means:

- tau 0.5: 0.2772
- tau 1.0: 0.2939
- tau 2.0: 0.3356
- tau 4.0: 0.3769

This audit is sensitivity-only. The main v0.6 config keeps its pre-specified tau and does not select tau from test results.

## v0.7 synthetic gene-prior sanity benchmark

Experiment ID: `v0.7-synthetic-gene-prior`

Command:

```powershell
python scripts/run_gene_prior.py --config configs/experiment/synthetic_v07_gene_prior.yaml
```

Latest output:

```text
outputs/runs/v0.7-gene-evolutionary-prior/synthetic_gene_prior/20260624T004215Z/
```

What this tests:

- `GenePriorTable` alignment and coverage behavior.
- `GenePriorCorrectionBaseline` plumbing over weak and strong base baselines.
- Prior audit, shuffled negative control, and prior-modulated subset reporting.

What this does not test:

- Real biological gene-prior utility.
- General evolutionary-prior effectiveness.
- SOTA, public leaderboard alignment, pathway priors, or neural EvoPrior.

## v0.7 Kang gene-prior compatibility benchmark

Experiment ID: `v0.7-kang-gene-prior-compatibility`

Commands:

```powershell
python scripts/prepare_gene_prior.py --config configs/priors/gene_prior_v07.yaml --dry-run
python scripts/run_gene_prior.py --config configs/experiment/real_v07_kang_gene_prior.yaml
```

Latest output:

```text
outputs/runs/v0.7-gene-evolutionary-prior/kang_2018_pbmc_ifnb/20260624T004226Z/
```

Source mode:

- `synthetic_gene_prior`
- engineering-only placeholder table generated from the Kang gene list

Interpretation:

- compatibility-only;
- real evolutionary-prior benefit was not tested;
- metrics must not be interpreted as biological discovery or general gene-prior effectiveness.

## v0.8 Kang HGNC metadata-prior ablation

Experiment ID: `v0.8-kang-real-gene-metadata-prior`

Commands:

```powershell
python scripts/prepare_gene_prior.py --config configs/priors/gene_prior_real_v08.yaml --dry-run
python scripts/prepare_gene_prior.py --config configs/priors/gene_prior_real_v08.yaml
python scripts/run_gene_prior.py --config configs/experiment/real_v08_kang_real_gene_prior.yaml
```

Latest output:

```text
outputs/runs/v0.8-real-versioned-gene-prior-source/kang_2018_pbmc_ifnb/20260624T010126Z/
```

Coverage report:

```text
outputs/data_reports/kang_2018_pbmc_ifnb/20260624T010126Z/real_gene_prior_v08_coverage_report.md
```

Source:

- mode: `download_hgnc`
- kind: `real_functional_gene_metadata`
- feature columns: `hgnc_gene_group_count`, `is_immune_related`, `approved_symbol_present`, `gene_biotype`, `locus_group`
- coverage over evaluated Kang genes: 1,875 / 2,000 = 93.75%

Metric summary:

- `lineage_shrinkage` and `gene_prior_correction_lineage_shrinkage` both have mean held-out-cell-type MAE 0.3160 and MSE 4.9515.
- `shuffled_gene_prior_correction_lineage` matches the lineage correction metrics.
- `gene_prior_correction_mean_delta` matches `mean_delta` on MAE 0.4317 and MSE 9.7610.
- `gene_prior_correction_control_mean` changes control mean metrics but does not improve MAE over `control_mean`.
- DE top-20 precision is 0.6295 for both `lineage_shrinkage` and `gene_prior_correction_lineage_shrinkage`.

Interpretation:

- real HGNC metadata-prior source and coverage plumbing work;
- this run does not support a performance gain over `lineage_shrinkage`;
- because no orthology/conservation source is configured, this is not evidence for real evolutionary/conservation-prior benefit.

## v0.9 integrated EvoPrior additive benchmark

Experiment IDs:

- `v0.9-synthetic-integrated-evoprior-additive`
- `v0.9-kang-evoprior-additive`

Commands:

```powershell
python scripts/run_evoprior_additive.py --config configs/experiment/synthetic_v09_integrated_evoprior.yaml
python scripts/run_evoprior_additive.py --config configs/experiment/real_v09_kang_evoprior_additive.yaml
```

Latest outputs:

```text
outputs/runs/v0.9-integrated-evoprior-additive/synthetic_integrated/20260624T015634Z/
outputs/runs/v0.9-integrated-evoprior-additive/kang_2018_pbmc_ifnb/20260624T015655Z/
```

Baselines:

- `control_mean`
- `mean_delta`
- `hierarchical_additive`
- `ridge_cv`
- `lineage_shrinkage`
- `gene_prior_correction_lineage_shrinkage`
- `evoprior_additive_no_gene_prior`
- `evoprior_additive_hgnc_gene_prior` or `evoprior_additive_synthetic_gene_prior`
- `evoprior_additive_shuffled_gene_prior`
- `evoprior_additive_gene_prior_disabled`

Kang metric summary:

- `evoprior_additive_hgnc_gene_prior`: mean MAE 0.3008, MSE 4.5008.
- `evoprior_additive_no_gene_prior`: mean MAE 0.3006, MSE 4.5011.
- `lineage_shrinkage`: mean MAE 0.3160, MSE 4.9515.

Interpretation:

- the integrated additive model improves over `lineage_shrinkage` on this Kang project split;
- the HGNC gene-prior component does not improve MAE over the no-gene-prior additive variant;
- the component audit is mostly lineage-dominated;
- this is not evidence for true evolutionary/conservation-prior benefit.

## v0.10 benchmark evidence alignment

Experiment IDs:

- `v0.10-synthetic-benchmark-alignment`
- `v0.10-kang-benchmark-alignment`

Commands:

```powershell
python scripts/run_benchmark_alignment.py --config configs/experiment/v10_benchmark_alignment_synthetic.yaml
python scripts/run_benchmark_alignment.py --config configs/experiment/v10_benchmark_alignment_kang.yaml
```

Latest outputs:

```text
outputs/runs/v0.10-public-benchmark-alignment/synthetic_alignment/20260624T021655Z/
outputs/runs/v0.10-public-benchmark-alignment/kang_2018_pbmc_ifnb_alignment/20260624T021659Z/
```

Artifacts:

- `benchmark_evidence.json`
- `benchmark_evidence_table.csv`
- `benchmark_evidence_report.md`

Interpretation:

- v0.10 aligns existing evidence records and marks missing artifacts without crashing;
- Kang alignment collected 40 records and all had finite metric status after n=0 empty metrics were treated as missing values;
- v0.9 integrated additive variants are comparable to `lineage_shrinkage` on the same Kang split;
- `evoprior_additive_hgnc_gene_prior` trails `evoprior_additive_no_gene_prior` on MAE, so HGNC gene-prior benefit is weak/not established;
- external public benchmark alignment remains blocked.

## v0.11 external public benchmark ingestion planning

Experiment ID: `v0.11-public-benchmark-ingestion-plan`

Command:

```powershell
python scripts/plan_public_benchmark_ingestion.py --config configs/experiment/v11_public_benchmark_ingestion_plan.yaml
```

Latest output:

```text
outputs/runs/v0.11-external-public-benchmark-ingestion/20260624T023024Z/
```

Artifacts:

- `public_benchmark_ingestion_plan.json`
- `public_benchmark_ingestion_table.csv`
- `public_benchmark_ingestion_report.md`

Summary:

- registered benchmark records: 2;
- blocked records: 2;
- local-fixture validated records: 0;
- no model was trained;
- no performance claim was produced;
- no external data was committed.

Interpretation:

- v0.11 creates a safe ingestion planning layer only;
- metadata-only records are not benchmark evidence;
- public benchmark claims remain blocked until data, split validation, model runs, and v0.10 evidence records exist.

## v0.12 public benchmark-compatible baseline run

Experiment ID: `v0.12-public-benchmark-baseline-run`

Commands:

```powershell
python scripts/prepare_public_benchmark.py --config configs/data/public_benchmark_v012.yaml --dry-run
python scripts/prepare_public_benchmark.py --config configs/data/public_benchmark_v012.yaml
python scripts/run_public_benchmark_baseline.py --config configs/experiment/public_benchmark_v012_baseline.yaml
```

Output:

```text
outputs/runs/v0.12-public-benchmark-baseline-run/scperturb_papalexi_2021_arrayed_rna_v012/20260624T150442Z/
```

Data report:

```text
outputs/data_reports/scperturb_papalexi_2021_arrayed_rna_v012/20260624T150442Z/
```

Benchmark status:

- public scPerturb-compatible Papalexi/Satija H5AD;
- custom leave-one-perturbation suite over guide-level pseudobulk groups;
- not official leaderboard aligned;
- internal compatible metrics only.

Baselines:

- `no_change`
- `control_mean`
- `mean_delta`
- `perturbation_mean_delta_v2`
- `hierarchical_additive`
- `ridge_cv`
- `evoprior_additive_no_prior`

Main test metrics:

- `no_change` and `control_mean`: MAE 0.2388, MSE 1.7221, DE top-20 precision 0.0000.
- `mean_delta`, `perturbation_mean_delta_v2`, `hierarchical_additive`, and `evoprior_additive_no_prior`: MAE 0.6922, MSE 5.7392, Pearson 0.5692, Spearman 0.3210, DE top-20 precision 0.5125.
- `ridge_cv`: MAE 0.7152, MSE 6.0478, Pearson 0.5656, Spearman 0.3181, DE top-20 precision 0.5125.

Interpretation:

- v0.12 proves the public-data baseline run is executable and auditable.
- The test suite is underpowered with only two held-out perturbations.
- Do not claim SOTA, official benchmark alignment, leaderboard comparability, biological discovery, or general EvoPrior superiority.

## v0.13 GEARS-compatible Norman baseline run

Experiment ID: `v0.13-gears-norman-baseline`

Commands:

```powershell
python scripts/prepare_gears_norman.py --config configs/data/gears_norman_v013.yaml --dry-run
python scripts/prepare_gears_norman.py --config configs/data/gears_norman_v013.yaml
python scripts/run_gears_norman_baseline.py --config configs/experiment/gears_norman_v013_baseline.yaml
```

Output:

```text
outputs/runs/v0.13-gears-norman-baseline/gears_norman_scperturb_v013/20260625T002742Z/
```

Data report:

```text
outputs/data_reports/gears_norman_scperturb_v013/20260625T002742Z/
```

Benchmark status:

- public Norman/scPerturb H5AD;
- GEARS-compatible internal combo split with seen0/seen1/seen2 labels;
- not official GEARS split;
- internal compatible metrics only;
- no neural GEARS model or leaderboard submission.

Baselines:

- `no_change`
- `control_mean`
- `mean_delta`
- `perturbation_mean_delta_v2`
- `single_effect_additive_combo`
- `ridge_cv`
- `evoprior_additive_no_prior`

Main test metrics:

- `control_mean`: MAE 0.8739, MSE 13.4469.
- `mean_delta`: MAE 0.5939, MSE 7.6769, Pearson 0.6450, Spearman 0.4920.
- `single_effect_additive_combo`: MAE 0.5491, MSE 6.1062, Pearson 0.7538, Spearman 0.5583.
- Combo-only `single_effect_additive_combo`: MAE 0.5938, MSE 6.5080, Pearson 0.8218, Spearman 0.6388.

Leakage audit:

- overall pass: true;
- leaked test combos: none;
- test groups: 33 combo groups and 31 single groups;
- test split classes: seen0=2, seen1=13, seen2=18, single_unseen=31.

Interpretation:

- v0.13 produces the first reproducible Norman/GEARS-compatible public benchmark baseline run in this repo.
- `single_effect_additive_combo` is the strongest implemented non-neural baseline under this exact internal split.
- Do not claim official GEARS alignment, leaderboard comparability, SOTA, neural GEARS reproduction, biological discovery, or general EvoPrior superiority.
