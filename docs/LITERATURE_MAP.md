# 文献地图

状态：初始种子地图。此文件不是完整综述；进入正式 benchmark 前需要逐条复核论文、代码、数据版本和评测设置。

## 扰动响应预测方法

| 方法/方向 | 核心思想 | 与本项目关系 | 初始来源 |
| --- | --- | --- | --- |
| scGen | VAE latent arithmetic 预测未见细胞类型/扰动响应 | 早期单细胞扰动预测基线，提醒我们关注跨细胞类型泛化 | Nature Methods: <https://www.nature.com/articles/s41592-019-0494-8> |
| CPA | 组合扰动自编码器，建模药物、剂量、细胞类型和组合 | 可作为非谱系先验的强表征基线候选 | Molecular Systems Biology: <https://link.springer.com/article/10.15252/msb.202211517> |
| GEARS | 图神经网络结合基因关系图，预测单/多基因扰动 | 与“网络/先验帮助外推”最直接相关 | Nature Biotechnology: <https://www.nature.com/articles/s41587-023-01905-6> |
| scGPT | 单细胞 foundation model，可微调用于 genetic perturbation prediction | 作为 foundation model 对照或特征提取候选，但必须严控泄漏 | Nature Methods: <https://www.nature.com/articles/s41592-024-02201-0> |
| Foundation model 扰动评测批评 | 近期研究指出深度/foundation 模型未必稳定优于朴素基线 | 强化本项目“先锁基线与评测”的必要性 | Nature Methods: <https://www.nature.com/articles/s41592-025-02772-6> |

## v0.3 真实数据来源

| 资源 | 要点 | 本项目使用策略 | 初始来源 |
| --- | --- | --- | --- |
| scPerturb | Harmonized single-cell perturbation data resource，提供多个 `.h5ad` 文件 | v0.3 使用其 Zenodo v1.4 H5AD 文件作为第一真实数据 plumbing 测试 | Project: <https://projects.sanderlab.org/scperturb/>；Zenodo: <https://zenodo.org/records/13350497> |
| PapalexiSatija2021 ECCITE-seq | stimulated THP-1 cell line 的 11 gRNA ECCITE-seq 数据 | 选择 arrayed RNA H5AD，体量小、control label 清楚；仅用于工程验证 | pertpy note: <https://pertpy.readthedocs.io/en/1.0.6/api/data/pertpy.data.papalexi_2021.html> |

## 基准与社区评测

| 资源 | 要点 | 本项目使用策略 | 初始来源 |
| --- | --- | --- | --- |
| Virtual Cell Challenge | 关注 context generalization 和 biologically meaningful metrics | 若可访问，作为优先公开基准候选；否则复刻其评测思想 | Evaluation: <https://virtualcellchallenge.org/evaluation> |
| CZI Virtual Cells Platform | 强调标准化、可复现、社区驱动的 benchmark | 用作数据/任务发现与评测设计参考 | Platform: <https://virtualcellmodels.cziscience.com/> |
| VCBench / in-the-wild benchmark | 关注 unseen context、unseen perturbation、跨数据集泛化 | 可作为后续严苛外推评测参照，需复核版本 | arXiv: <https://arxiv.org/abs/2604.27646> |

## 本项目需要特别警惕的坑

- 不同论文的 preprocessing、基因集合、split、metric 差异很大，不能横向硬比。
- 用 post-perturbation test expression 生成 embedding 或 prior 会造成严重泄漏。
- 在同一个扰动或同一 donor 同时出现在训练和测试时，某些“泛化”声称不成立。
- top DE gene 指标可能受 DE 方法、基因过滤、pseudobulk 聚合和 batch correction 强烈影响。
- foundation model 结果必须区分“预训练知识”“训练数据泄漏”和“真正外推”。

## 下一步文献任务

1. 为选定第一个数据集补齐原始论文、数据下载地址、license 和已知 benchmark split。
2. 建立 baseline 复现表：no-change、mean、additive、ridge、scGen、CPA、GEARS、公开 leaderboard 方法。
3. 为每个指标写出数学定义和与 Virtual Cell Challenge/CZI benchmark 的对应关系。
