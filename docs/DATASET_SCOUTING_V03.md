# v0.3 数据集侦察记录

状态：v0.3 已选择一个小型真实公开数据集，用于验证真实数据 ingestion 和 baseline plumbing。

## 选择原则

- 文件小于 2GB，优先远小于 2GB。
- 公开可访问，最好是 AnnData/H5AD。
- 有清晰 perturbation 和 control labels。
- 能形成至少一个 held-out perturbation split。
- 尽量少做自定义 preprocessing。
- 不以“名气”优先，而以“可信真实数据闭环最快”优先。

## 候选表

| Dataset | Source | Modality | Perturbation type | Approx size | Format | Controls? | Cell type? | Donor/batch? | Access/license | Expected split | Risks | v0.3 decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PapalexiSatija2021 ECCITE-seq arrayed RNA | scPerturb Zenodo v1.4 | scRNA-seq | CRISPR perturbation, THP-1 stimulated cell line | 52.3 MB | `.h5ad` | Yes, `control` | Yes, one `monocytes` label | No donor/batch | CC-BY-4.0 via Zenodo | random group + held-out `pdl1` | One cell type; small number of pseudobulk groups; not a published benchmark split | selected |
| DatlingerBock2021 | scPerturb Zenodo v1.4 | scRNA-seq | CRISPR/CROP-seq style perturbation | 33.6 MB | `.h5ad` | likely, needs inspection | likely limited | unknown before download | CC-BY-4.0 via Zenodo | held-out perturbation | Need metadata inspection; less immediately documented in this repo | backup |
| NormanWeissman2019 filtered | scPerturb Zenodo v1.4 | scRNA-seq | CRISPRa pooled perturbation | 698.7 MB | `.h5ad` | likely | one cell line | likely no donor | CC-BY-4.0 via Zenodo | held-out perturbation / combinations | Larger file; better suited after v0.3 plumbing is stable | future |
| Parse PBMC cytokine / Virtual Cell Challenge | Parse/VCC | scRNA-seq | cytokine perturbations | large | likely H5AD / challenge format | yes | many PBMC cell types | donors available | challenge-specific access | held-out context/cell type/donor | Too large/complex for first real-data plumbing milestone | future |

## v0.3 决策

选择 `scperturb_papalexi_2021_arrayed_rna`，因为它是公开 H5AD、体量很小、control labels 清楚、metadata 足以映射到 canonical schema，并且可以构造 held-out perturbation split。

这个选择的科学边界很窄：它不能测试谱系泛化、donor 泛化或多组织泛化；它只证明 EvoPrior-AIVC 的真实数据读取、schema mapping、pseudobulk、split、baseline、metrics 和 report 输出能在一个真实 perturbation 数据集上跑通。

## 来源

- scPerturb Zenodo record: <https://zenodo.org/records/13350497>
- Papalexi/pertpy dataset note: <https://pertpy.readthedocs.io/en/1.0.6/api/data/pertpy.data.papalexi_2021.html>
- scPerturb project: <https://projects.sanderlab.org/scperturb/>

