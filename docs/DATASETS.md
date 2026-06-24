# 数据集

状态：v0.6 已接入一个小型真实 multi-cell-type benchmark；候选清单继续保留用于后续扩展。

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

## v0.2 synthetic fixture

v0.2 新增 `src/evoprior_aivc/data/synthetic.py`，用于生成工程验证专用的 AnnData 对象。该 fixture 包含：

- 3 个 cell types：`t_cell`、`b_cell`、`monocyte`。
- 4 个 perturbations：`control`、`pert_a`、`pert_b`、`pert_c`。
- 2 个 donors：`donor_1`、`donor_2`。
- 至少 20 个 genes。
- 已知扰动 delta pattern 和少量 cell-type-specific effect。
- 足够细胞数用于 pseudobulk mean aggregation。

该数据只用于验证 schema、pseudobulk、split、baseline、metrics 和 artifact 保存是否连通。它不能支持任何生物学声称，也不能作为真实 benchmark 结果。

## 未来真实 AnnData/H5AD 期望格式

`.obs` 必需字段：

- `cell_type`
- `perturbation`
- `is_control`

`.obs` 推荐字段：

- `donor`
- `batch`
- `tissue`
- `dose`
- `time`

`.var` 至少应包含：

- `gene_symbol` 或 `gene_id`

`.var` 推荐字段：

- `highly_variable`
- `gene_biotype`

v0.2 没有下载任何大型公开数据集。下一阶段 v0.3 才会接入真实公开扰动数据，并记录数据版本、checksum、license、schema 适配和 split 定义。

## v0.3 selected real dataset

Dataset ID: `scperturb_papalexi_2021_arrayed_rna`

Display name: PapalexiSatija2021 ECCITE-seq arrayed RNA

Source: scPerturb Zenodo record v1.4, file `PapalexiSatija2021_eccite_arrayed_RNA.h5ad`.

Access:

- URL: <https://zenodo.org/records/13350497>
- Direct file configured in `configs/data/real_v03.yaml`
- Expected local path: `data/raw/PapalexiSatija2021_eccite_arrayed_RNA.h5ad`
- File size: 52,339,395 bytes
- md5: `843820d48b024348d6132cd53be0da91`
- License: CC-BY-4.0 via Zenodo

Observed raw shape:

- Cells: 8,984
- Genes: 16,826

Raw obs fields used:

- `perturbation` -> canonical `perturbation`
- `celltype` -> canonical `cell_type`
- `tissue_type` -> canonical `tissue`
- `guide_id` preserved for guide-level pseudobulk grouping
- `cell_line`, `hto`, `perturbation_type`, `nperts` preserved as auxiliary metadata

Raw var fields used:

- `var_names` -> canonical `gene_symbol`
- `ensembl_id` -> canonical `gene_id`

Control mapping:

- `is_control` is inferred from `perturbation in {"control", "ctrl", "nt", "non-targeting"}`.
- Observed controls: 2,009 cells.

Preprocessing in v0.3:

- No advanced normalization is introduced.
- Active `X` from the H5AD is used.
- Genes expressed in fewer than 10 cells are filtered.
- Top 3,000 genes by variance are retained for a local baseline smoke run.
- Pseudobulk grouping uses `cell_type`, `perturbation`, and `guide_id`.
- Groups with fewer than 20 cells are dropped.

Limitations:

- Only one cell type/cell line is present: `monocytes` / THP-1.
- No donor or batch field is available.
- `IFNGR2` has only 4 cells and is dropped by the v0.3 pseudobulk threshold.
- The split is project-defined, not a published benchmark split.
- This dataset validates real-data plumbing only; it does not test lineage or donor generalization.

## v0.4 preprocessing sensitivity notes

v0.4 audits a compact preprocessing matrix:

- top variance genes: 1000, 3000, 5000
- min cells per pseudobulk group: 10, 20, 50
- split modes: random_group and heldout_pdl1

The sensitivity audit is descriptive. It must not be used to choose hyperparameters on test metrics or to claim biological superiority.

## v0.6 selected real multi-cell-type dataset

Dataset ID: `kang_2018_pbmc_ifnb`

Display name: Kang et al. 2018 PBMC IFN-beta stimulation

Source:

- Figshare article: <https://figshare.com/articles/dataset/Kang_HM_Subramaniam_M_Targ_S_Nguyen_M_et_al_2017/19397624>
- Direct file configured in `configs/data/real_multicell_v06.yaml`
- pertpy loader documentation: <https://pertpy.readthedocs.io/en/latest/api/data/pertpy.data.kang_2018.html>

Access:

- Expected local path: `data/raw/kang_2018_pbmc_ifnb.h5ad`
- File size: 38,356,412 bytes
- md5: `adb2246232e8493031c576982c0c02a3`
- Format: H5AD
- Auto-download allowed because the file is well below 2 GB and checksum is configured.

Observed raw shape after adapter load:

- Cells: 24,673
- Genes: 15,706
- Cell types: 8
- Perturbation labels: `ctrl`, `stim`
- Controls: 12,315 cells

Raw obs fields used:

- `label` -> canonical `perturbation`
- `cell_type` -> canonical `cell_type`
- `replicate` -> canonical `donor`
- `nCount_RNA`, `nFeature_RNA`, `cluster`, `seurat_clusters` preserved as auxiliary metadata

Raw var fields used:

- `name` -> canonical `gene_symbol`

v0.6 preprocessing:

- Active `X` is used.
- Genes expressed in fewer than 10 cells are filtered.
- Top 2,000 genes by variance are retained.
- Pseudobulk grouping uses `cell_type`, `perturbation`, and `donor`.
- Minimum cells per pseudobulk group is 5 to preserve donor-matched control/stim pairs for rare PBMC subsets.

Suitability result:

- Pass for first real multi-cell-type held-out cell-type lineage benchmark.
- 7 cell types are eligible after pseudobulk filtering.
- `megakaryocytes` is skipped because it has too few test groups.
- Only one non-control perturbation exists, so retrieval/PDS is not meaningful and general multi-perturbation claims are not allowed.

## v0.7 Kang gene-prior compatibility note

The v0.7 Kang gene-prior runner reuses `kang_2018_pbmc_ifnb` for engineering compatibility only.

- Config: `configs/experiment/real_v07_kang_gene_prior.yaml`
- Gene-prior config: `configs/priors/gene_prior_kang_v07.yaml`
- Current source mode: `synthetic_gene_prior`
- Latest compatibility output: `outputs/runs/v0.7-gene-evolutionary-prior/kang_2018_pbmc_ifnb/20260624T004226Z/`

Because the configured prior is synthetic/placeholder, this dataset run does not test real evolutionary-prior benefit.
