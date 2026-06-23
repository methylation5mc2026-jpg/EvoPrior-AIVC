# 已知失败与风险

## 当前已知风险

1. 尚未锁定第一公开数据集；所有 benchmark 描述都是设计约束，不是已完成实验。
2. 文献地图是初始种子，未完成系统综述。
3. 当前指标实现只覆盖最小玩具案例；真实单细胞评测需要补充 per-group breakdown、DE 方法和置信区间。
4. 当前切分实现只做基础 held-out 标签检查；复杂 context split 需要更严格的组合键审计。
5. 还没有下载、校验或处理任何 AnnData 文件。

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
