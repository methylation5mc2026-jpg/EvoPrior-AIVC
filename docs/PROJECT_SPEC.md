# 项目规格

## 目标

EvoPrior-AIVC 要构建一个可复现、可审计的单细胞扰动响应预测研究项目。第一阶段目标是做出可信的最小基线系统，而不是先做大型神经网络。

## 输入与输出

输入：

- 对照单细胞表达或 pseudobulk 表达。
- 扰动身份与扰动元数据。
- 细胞类型、供体、批次、组织或实验上下文。
- 可选生物先验：细胞谱系、基因保守性、通路/调控网络。

输出：

- 扰动后表达。
- delta expression。
- top DE genes。
- 扰动辨别排序。
- 不确定性或置信分数。
- conserved/core、lineage-shared、cell-type-specific、residual 分解。

## 核心假设

真实细胞不是扁平 token。扰动响应受到历史约束：细胞谱系、基因演化保守性、既往扰动响应、调控网络拓扑和当前细胞状态共同塑造响应。

项目要检验结构化历史先验是否在以下场景提升外推能力：

- held-out cell types。
- held-out donors。
- held-out perturbations。
- held-out cell contexts。

## 当前定义的响应分解

```text
response_delta =
    conserved_core_response
  + lineage_shared_response
  + cell_type_specific_response
  + donor/state/batch residual
```

## 当前里程碑状态

- v0.2: synthetic AnnData pipeline、pseudobulk、基础 baseline、split/metric/report 闭环。
- v0.3: 第一个真实公开 H5AD perturbation dataset 接入和真实 baseline runner。
- v0.4: 更强 classical baselines、重复 split、置信区间、perturbation retrieval、DE recovery、预处理敏感性审计和公开 benchmark alignment。
- v0.5: 第一个细胞谱系先验基础设施模块，包括 lineage tree、cell-type mapping、lineage features、synthetic multi-cell-type lineage benchmark 和 non-neural `LineageShrinkageBaseline`。

v0.5 仍不包含 EvoPrior 神经模型、演化先验或通路先验。下一阶段 v0.6 应先选择真实 multi-cell-type perturbation benchmark，再谈真实谱系泛化证据。

## 内部角色

- 研究负责人：定义假设、基准、可声称范围。
- 数据工程师：维护 AnnData/pseudobulk/metadata pipeline。
- 基线工程师：实现 no-change、mean、additive、ridge 等基线。
- 模型工程师：在基线闭环后实现 EvoPrior 变体。
- 评测工程师：维护指标、泄漏检查和报告。
- MLOps 工程师：维护配置、日志、checkpoint 和回滚。
- 科学审稿人：检查生物学和统计声称是否成立。

## 质量门

Gate A 数据有效性：

- 数据可加载。
- 必需 obs/var 字段存在。
- 扰动标签归一化。
- 对照条件可识别。
- 细胞类型、供体、批次字段显式存在。
- 缺失值被报告。

Gate B 切分有效性：

- held-out perturbations 不出现在训练/验证中。
- held-out cell types 不出现在训练/验证中。
- donor split 下 held-out donors 不出现在训练/验证中。
- 不用测试集 post-perturbation expression 生成先验或 embedding。

Gate C 基线有效性：

- no-change、mean、additive、ridge 基线能运行。
- 基线指标保存。
- 每份报告都包含基线。

Gate D 模型有效性：

- forward pass shape 测试通过。
- tiny overfit 子集 loss 下降。
- 预测有限且无 silent NaN。
- checkpoint 重新加载后预测可复现。

Gate E 评测有效性：

- 指标在合成已知案例上测试。
- 模型比较前锁定 evaluation script。
- 尽可能报告 seed variation 或 confidence interval。

Gate F 科学有效性：

- 声称分为“实验已证明”“消融提示”“未来推测”。
- 没有直接基准证据时不声称 SOTA。
- 可解释性声称必须给出具体基因、通路或细胞类型。

## 当前 v0.5 完成标准

- 项目文档和目录结构存在。
- 最小指标测试通过。
- 最小切分泄漏测试通过。
- v0.2/v0.3/v0.4 baseline loop 保持可运行。
- v0.5 lineage prior infrastructure 和 synthetic lineage sanity benchmark 有测试和 runner。
- Papalexi compatibility run 明确记录 single-cell-type/no-op 限制。
- 不声称真实生物谱系有效性、SOTA、near-SOTA 或 EvoPrior neural model。
