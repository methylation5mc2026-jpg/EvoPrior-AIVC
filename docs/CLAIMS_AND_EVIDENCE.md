# 声称与证据

## 原则

本项目所有科学和性能声称必须指向实验 ID。没有实验 ID 的内容只能作为计划、假设或未来工作。

## 已证明

- `v0.2-synthetic-baseline-smoke`: 仓库可以运行完整 synthetic perturbation baseline loop，包括 schema validation、pseudobulk aggregation、random/heldout split、四个 baseline、metrics JSON、prediction CSV、split assignment 和 markdown report。
- `v0.2-synthetic-baseline-smoke`: 在 synthetic smoke test 中，四个 baseline 都能产生有限预测和指标。这是工程级证据，不是生物学证据。
- `v0.3-real-benchmark-baselines`: 项目支持一个真实公开 perturbation H5AD 数据集通过 canonical schema。证据：`scperturb_papalexi_2021_arrayed_rna` adapter schema report。
- `v0.3-real-benchmark-baselines`: baseline evaluation loop 可以在真实数据上端到端运行，并生成 metrics、predictions、split manifest、schema report、failure cases 和 markdown report。
- `v0.3-real-benchmark-baselines`: selected held-out perturbation split 的 leakage check 通过；`pdl1` 不出现在训练/验证 split 中。
- `v0.4-real-baseline-strengthening`: repeated real-data baseline evaluation works and writes per-run metrics, metric summaries, confidence intervals, retrieval summaries, DE summaries, skipped perturbations, and a v0.4 report.
- `v0.4-real-baseline-strengthening`: perturbation-level retrieval metrics and DE recovery metrics are implemented with unit tests.
- `v0.4-real-baseline-strengthening`: preprocessing sensitivity audit runs over a compact matrix and reports metric fragility.
- `docs/PUBLIC_BENCHMARK_ALIGNMENT_V04.md`: current v0.4 setup has been audited and is explicitly not public-benchmark-aligned.
- `v0.5-synthetic-lineage-prior`: lineage tree infrastructure, cell-type-to-lineage mapping, lineage distance/features, synthetic multi-cell-type lineage data generation, and one non-neural lineage-aware baseline are implemented with tests.
- `v0.5-synthetic-lineage-prior`: on a known synthetic lineage-structured generator, `lineage_shrinkage` can be evaluated against v0.4-style classical baselines under held-out cell-type splits. This is synthetic logic validation only.
- `v0.5-papalexi-lineage-compatibility`: the lineage baseline runs safely on the existing Papalexi real-data plumbing in compatibility/no-op mode, and the report records that lineage signal is not identifiable with one configured cell type.
- `v0.6-real-multicell-lineage-benchmark`: a real multi-cell-type PBMC IFN-beta benchmark is implemented on `kang_2018_pbmc_ifnb` with documented schema mapping, coarse lineage mapping, held-out cell-type splits, leakage checks, v0.4 baselines, and v0.5 `lineage_shrinkage`.
- `v0.6-real-multicell-lineage-benchmark`: on this dataset and project-defined held-out cell-type suite, `lineage_shrinkage` improves mean test MAE/MSE/Pearson/Spearman over the configured v0.4 classical baselines. Output: `outputs/runs/v0.6-real-multicell-lineage-benchmark/kang_2018_pbmc_ifnb/20260623T092131Z/`.
- `v0.6-real-multicell-lineage-tau-audit`: pre-specified tau values were audited as sensitivity only. Output: `outputs/runs/v0.6-real-multicell-lineage-tau-audit/kang_2018_pbmc_ifnb/20260623T092131Z/`.
- `v0.7-synthetic-gene-prior`: `GenePriorTable`, synthetic gene-prior data generation, `GenePriorCorrectionBaseline`, prior audit, shuffled negative control, and v0.7 runner plumbing are implemented and tested. Output: `outputs/runs/v0.7-gene-evolutionary-prior/synthetic_gene_prior/20260624T004215Z/`.
- `v0.7-kang-gene-prior-compatibility`: Kang gene-prior feature mapping, coverage, correction runner, and report generation run end-to-end with an engineering-only synthetic/placeholder prior. Output: `outputs/runs/v0.7-gene-evolutionary-prior/kang_2018_pbmc_ifnb/20260624T004226Z/`.

## 消融提示

- `v0.5-synthetic-lineage-prior`: synthetic held-out cell-type results can be used as an implementation sanity check for lineage borrowing. They cannot be promoted to real-data biological evidence.
- `v0.6-real-multicell-lineage-benchmark`: held-out lineage suite has only n=2 clades and is underpowered; treat it as diagnostic context only.
- `v0.7-synthetic-gene-prior`: synthetic prior-modulated effects validate plumbing and ablation logic only.
- `v0.7-kang-gene-prior-compatibility`: because the source mode is `synthetic_gene_prior`, Kang v0.7 is compatibility-only and does not test real evolutionary-prior benefit.

## 推测/未来工作

- 细胞谱系先验可能提升真实 held-out cell type 或 held-out context 外推，但还需要 v0.6 真实 multi-cell-type perturbation benchmark 验证。
- 基因演化/保守性先验可能提升 held-out perturbation 外推。
- 通路/调控网络先验可能提升 top DE gene recovery。
- v0.8 可以在 v0.7 工程闭环稳定后引入真实、版本化 gene-prior source。

这些都需要在固定 benchmark、统一 baselines 和多 seed 实验后才能升级为证据性声称。

## 明确不声称

- 不声称任何真实公开数据集性能。
- 不声称 SOTA 或 near-SOTA。
- 不声称 lineage prior 已经在真实生物数据上有效；v0.5 只实现了第一个非神经谱系先验 baseline 和 synthetic sanity check。
- 不声称真实 evolutionary-prior benefit、pathway prior 或 neural EvoPrior 已经实现。
- 不声称 v0.3 的 Papalexi split 是公开 leaderboard 或论文 benchmark。
- 不声称真实数据指标说明生物学发现；它们只说明当前 pipeline 可以运行。
- 不声称 v0.4 repeated metrics establish model superiority; leave-one perturbation is underpowered.
- 不声称 retrieval/PDS is meaningful for held-out perturbations absent from train candidate profiles.
- 不声称 Papalexi v0.5 compatibility metrics 说明谱系先验有效；该数据在当前配置下只有一个 cell type/cell line。
- 不声称 v0.6 Kang result generalizes beyond PBMC IFN-beta stimulation.
- 不声称 v0.6 is public-leaderboard comparable.
- 不把 tau audit 中测试集表现最好的 tau 当作调参选择结果。
- 不声称 v0.7 Kang metrics 说明 real evolutionary-prior benefit；当前 prior 是 synthetic/placeholder。
