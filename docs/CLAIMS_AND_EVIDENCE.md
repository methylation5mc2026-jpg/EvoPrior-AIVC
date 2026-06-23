# 声称与证据

## 原则

本项目所有科学和性能声称必须指向实验 ID。没有实验 ID 的内容只能作为计划、假设或未来工作。

## 已证明

- `v0.2-synthetic-baseline-smoke`: 仓库可以运行完整 synthetic perturbation baseline loop，包括 schema validation、pseudobulk aggregation、random/heldout split、四个 baseline、metrics JSON、prediction CSV、split assignment 和 markdown report。
- `v0.2-synthetic-baseline-smoke`: 在 synthetic smoke test 中，四个 baseline 都能产生有限预测和指标。这是工程级证据，不是生物学证据。
- `v0.3-real-benchmark-baselines`: 项目支持一个真实公开 perturbation H5AD 数据集通过 canonical schema。证据：`scperturb_papalexi_2021_arrayed_rna` adapter schema report。
- `v0.3-real-benchmark-baselines`: baseline evaluation loop 可以在真实数据上端到端运行，并生成 metrics、predictions、split manifest、schema report、failure cases 和 markdown report。
- `v0.3-real-benchmark-baselines`: selected held-out perturbation split 的 leakage check 通过；`pdl1` 不出现在训练/验证 split 中。

## 消融提示

暂无。

## 推测/未来工作

- 细胞谱系先验可能提升 held-out cell type 或 held-out context 外推。
- 基因演化/保守性先验可能提升 held-out perturbation 外推。
- 通路/调控网络先验可能提升 top DE gene recovery。

这些都需要在固定 benchmark、统一 baselines 和多 seed 实验后才能升级为证据性声称。

## 明确不声称

- 不声称任何真实公开数据集性能。
- 不声称 SOTA 或 near-SOTA。
- 不声称 lineage/evolutionary prior 已经有效；v0.2 尚未实现这些先验。
- 不声称 v0.3 的 Papalexi split 是公开 leaderboard 或论文 benchmark。
- 不声称真实数据指标说明生物学发现；它们只说明当前 pipeline 可以运行。
