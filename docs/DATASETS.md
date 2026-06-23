# 数据集

状态：候选清单。v0.1 尚未下载任何大型数据，也未锁定最终 benchmark。

## 候选数据集

| 数据集 | 扰动类型 | 优点 | 风险/成本 | 初始来源 |
| --- | --- | --- | --- | --- |
| Parse PBMC cytokine / Virtual Cell Challenge data | 90 cytokine perturbations，PBMC，12 donors，约 18 cell types | 非常适合 donor/cell-type/context 外推；与 AIVC 社区基准接近 | 数据体量大；需要确认下载方式、license、官方 split | Parse: <https://www.parsebiosciences.com/datasets/10-million-human-pbmcs-in-a-single-experiment/>；VCC data: <https://virtualcellchallenge.org/datasets> |
| Replogle et al. 2022 | CRISPRi，K562/RPE1，大规模 Perturb-seq | 有 AnnData 格式处理数据；适合基因扰动基线 | 细胞类型上下文较少，不适合谱系先验第一验证 | Figshare: <https://plus.figshare.com/articles/dataset/_Mapping_information-rich_genotype-phenotype_landscapes_with_genome-scale_Perturb-seq_Replogle_et_al_2022_processed_Perturb-seq_datasets/20029387> |
| Norman et al. 2019 | 组合遗传扰动 | 经典 Perturb-seq 组合扰动数据；常用于 GEARS 等方法 | 主要是单一细胞系，谱系/供体维度弱 | Science: <https://www.science.org/doi/10.1126/science.aax4438> |
| Tahoe-100M | 小分子扰动，多癌细胞系，超大规模 | 规模和 context 多样性强，适合后期大模型/系统评测 | 体量极大，本地硬件与存储风险高；不适合作为第一最小闭环 | bioRxiv: <https://www.biorxiv.org/content/10.1101/2025.02.20.639398v1> |

## v0.1 数据原则

- 先用小规模或可抽样数据闭环，不直接下载超大数据。
- 优先选择可公开访问、可记录 checksum、可用 AnnData 或容易转换为 AnnData 的数据。
- 数据字段最少要包含：perturbation、control indicator、cell_type、donor 或 batch、gene identifiers。
- 如果没有 donor/cell_type 维度，只能作为基线工程 smoke test，不能支撑谱系先验声称。

## 待锁定 schema

AnnData `.obs` 建议字段：

- `perturbation`
- `is_control`
- `cell_type`
- `donor`
- `batch`
- `tissue`
- `split`

AnnData `.var` 建议字段：

- `gene_id`
- `gene_symbol`
- `is_highly_variable`
- 后续可选：`gene_age`、`conservation_score`、`pathway_membership`

## 数据不提交规则

`data/raw/`、`data/interim/`、`data/processed/` 只放本地数据和 `.gitkeep`。真实数据下载脚本、checksum 和版本元数据应写入代码与实验台账。
