# 已知失败与风险

## 当前已知风险

1. 尚未锁定第一公开数据集；所有 benchmark 描述都是设计约束，不是已完成实验。
2. 文献地图是初始种子，未完成系统综述。
3. 当前指标实现只覆盖最小玩具案例；真实单细胞评测需要补充 per-group breakdown、DE 方法和置信区间。
4. 当前切分实现只做基础 held-out 标签检查；复杂 context split 需要更严格的组合键审计。
5. 还没有下载、校验或处理任何 AnnData 文件。
6. v0.2 只验证 synthetic data pipeline 和 baseline plumbing；真实 benchmark 尚未验证。
7. v0.2 的 `heldout_perturbation` 只测试 synthetic `pert_c` fallback，不代表真实 unseen perturbation 泛化能力。
8. 尚未实现 EvoPrior 模块、细胞谱系先验、基因保守性先验或通路网络先验。
9. 当前 preprocessing 尚未与任何公开论文 baseline 完全对齐。
10. v0.3 选择的 Papalexi/scPerturb 数据只有一个 cell type/cell line，不能测试谱系泛化。
11. v0.3 数据没有 donor 字段，不能测试 donor split。
12. v0.3 使用 project-defined split，没有与 Papalexi、scPerturb、pertpy 或 GEARS 的公开 split 对齐。
13. v0.3 held-out `pdl1` 只有两个 guide-level pseudobulk groups，其中一个 group 只有 24 cells，指标波动会很大。
14. v0.3 使用 top-variance 3,000 genes 的本地 smoke 配置，不代表完整基因空间评测。
15. v0.4 leave-one-perturbation suite is underpowered: only perturbations with at least two guide-level groups are eligible.
16. v0.4 retrieval metrics are not meaningful for held-out perturbations absent from train candidate profiles; these rows are marked underpowered/not meaningful.
17. v0.4 confidence intervals use a simple normal approximation and are descriptive only.
18. v0.4 sensitivity audit shows MAE can move substantially across top-gene and min-cell settings; this setup should not be optimized against test metrics.
19. Public benchmark alignment remains incomplete; current Papalexi split is not a GEARS/CZI/Systema/CPA/scGen benchmark.

## 失败记录模板

```text
Failure ID:
Date:
Experiment ID:
Symptom:
Root cause:
Evidence:
Impact:
Mitigation:
Preserved artifacts:
Rollback note:
```
