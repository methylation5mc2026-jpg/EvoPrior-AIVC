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
