# v0.5 真实多细胞数据集侦察

Status: scouting note only. Checked on 2026-06-23. v0.5 does not download or benchmark any new large real dataset.

## 目标

v0.5 已经实现第一个非神经 lineage-aware baseline，但真实生物有效性必须等到 v0.6 以后在真实 multi-cell-type perturbation 数据上验证。本文件只记录候选方向、准入条件和当前不下载的原因。

## 准入条件

真实 lineage-prior benchmark 至少需要：

- 多个可映射到稳定 ontology 或显式层级的 cell types、cell lines 或 states。
- 同一 perturbation 至少覆盖多个 context，便于 held-out cell type / held-out lineage / held-out donor split。
- 明确 control 条件、扰动标签、batch/donor/replicate 字段。
- 可复现下载入口、版本、checksum 或稳定 release。
- v0.4 baseline 可以在同一 preprocessing、gene set、split 和 metric 下重跑。

如果候选数据只有多个 cell lines 而没有发育谱系关系，只能称为 context/cell-line transfer；不能写成严格 biological lineage validation。

## 候选记录

| 候选 | 目前看到的优点 | v0.5 不采用的原因 | v0.6 下一步 |
| --- | --- | --- | --- |
| Virtual Cell Challenge / PBMC cytokine 数据 | 官方页面描述 PBMC perturbation 数据含 12 donors、18 cell types、90 cytokine responses；很适合测试 immune cell context 和 donor/context generalization。 | 当前轮不新增大数据下载；cytokine perturbation 与本项目现有 genetic perturbation runner 需要 schema 适配；需确认许可、文件大小和可程序化下载方式。 | 优先侦察。先做 dry-run metadata reader、体量检查、cell type ontology mapping，再定义 held-out cell type / donor split。 |
| scPerturb / pertpy 数据集合 | scPerturb 论文描述 44 个 harmonized public single-cell perturbation-response datasets；pertpy 提供多个 curated dataset loader，便于快速筛选小型候选。 | 集合内很多经典数据是单一 K562/细胞系，不适合谱系验证；需要逐个确认 cell_type、donor、control 和扰动覆盖。 | 写一个只读 metadata audit，按 `n_cell_types > 1`、`n_perturbations`、`has_control`、`download_size` 排序。 |
| Tahoe-100M / Arc Virtual Cell Atlas | Arc 新闻稿描述 Tahoe-100M 覆盖 50 cancer cell lines 和 1,200 drug perturbations，规模和 context 多样性强。 | 明显超过 v0.5 允许的轻量范围；cell line hierarchy 不是天然发育谱系；不经用户确认不下载。 | 只在明确需要大规模 cell-line context benchmark 且用户批准体量后考虑。 |
| Virtual Cell Challenge H1 hESC genetic benchmark | Cell commentary 描述 inaugural challenge 关注 H1 hESC genetic perturbation，训练/验证/测试 split 和 DE/PDS/MAE 指标更接近公开 benchmark。 | 首届任务核心是 H1 单一 cell type 内 few-shot perturbation prediction，不是多细胞谱系验证。 | 可作为公开评测协议学习对象，但不作为 v0.6 lineage-prior 首选。 |
| Replogle / Norman / Adamson 等经典 Perturb-seq | 与 GEARS、CPA、scGen 等文献生态连接强，适合对齐公开 perturbation prediction 任务。 | 多数经典设置以单一细胞系或少数 cell lines 为主，不能直接证明 lineage prior。 | 继续作为 benchmark alignment 候选；若选择，声称应限定为 perturbation/context transfer。 |

## 推荐 v0.6 顺序

1. 先做 Virtual Cell Challenge / PBMC cytokine 数据的 metadata-only audit，不下载大体量表达矩阵。
2. 并行扫描 pertpy/scPerturb loader 列表，寻找小于 2GB、含多个真实 cell types、可本地快速 smoke test 的候选。
3. 只有当 metadata 显示同一 perturbation 覆盖多个 cell types 且 control 完整时，才写 v0.6 data config。
4. 对每个候选先运行 v0.4 baselines，再运行 v0.5 `lineage_shrinkage`，并加入 lineage ablation。

## 来源

- Virtual Cell Challenge datasets: <https://virtualcellchallenge.org/datasets>
- Virtual Cell Challenge evaluation: <https://virtualcellchallenge.org/evaluation>
- scPerturb Nature Methods article: <https://experiments.springernature.com/articles/10.1038/s41592-023-02144-y>
- pertpy dataset index: <https://pertpy.readthedocs.io/en/stable/api/datasets_index.html>
- Arc/Tahoe-100M announcement: <https://arcinstitute.org/news/arc-vevo>
- Virtual Cell Challenge Cell commentary DOI: <https://doi.org/10.1016/j.cell.2025.06.008>
