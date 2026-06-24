# EvoPrior-AIVC

EvoPrior-AIVC 是一个面向单细胞扰动响应预测的研究工程项目。目标不是做泛泛的“AI for biology”演示，而是在明确公开数据集、固定切分、统一评测脚本和可复现实验记录之上，检验“细胞谱系先验、基因演化/保守性先验、通路/网络先验是否能提升外推预测”这个窄而严肃的问题。

当前仓库已推进到 v0.9-integrated-evoprior-additive-model：在 v0.8 HGNC metadata source 之上，新增透明、非神经的 `EvoPriorAdditiveModel`，把 global、perturbation、lineage 和可选 gene metadata residual 组件合成到同一 runner，并生成 component audit。v0.9 不包含 neural EvoPrior，不声称 SOTA，不声称真实 evolutionary/conservation-prior benefit，因为当前真实源不含 orthology、conservation score 或 gene-age 特征。

## 科学问题

给定对照表达、扰动身份、细胞类型/供体/批次/组织上下文，以及可选生物先验，预测扰动后的表达、表达变化、差异表达基因恢复、扰动排序和不确定性。

核心假设：

```text
response_delta =
    conserved_core_response
  + lineage_shared_response
  + cell_type_specific_response
  + donor/state/batch residual
```

## 当前完成范围

- 中文项目规范文档和初始文献/数据集/基准记录。
- Python `src/` 包骨架。
- 最小评测指标实现。
- 最小 held-out 切分与泄漏检查实现。
- 玩具测试，覆盖指标和切分泄漏规则。

## 安装与测试

建议先创建独立环境：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pytest
```

如果暂时不安装包，也可以在仓库根目录直接运行：

```powershell
python -m pytest
```

`pyproject.toml` 已配置 `src` 为测试导入路径。

## v0.2 Quickstart

安装依赖：

```powershell
python -m pip install -e ".[dev]"
```

运行所有测试：

```powershell
python -m pytest
```

运行 synthetic baseline smoke experiment：

```powershell
python scripts/run_baseline.py --config configs/experiment/synthetic_v02.yaml
```

输出会写入：

```text
outputs/runs/v0.2-synthetic-baseline-smoke/<timestamp>/
```

该目录包含 `resolved_config.yaml`、`metrics.json`、`metrics.csv`、`predictions.csv`、`split_assignments.csv`、`schema_report.json`、`report.md` 和 `log.txt`。这些是本地运行产物，不提交到 git。

## v0.3 Quickstart

先查看真实数据准备计划：

```powershell
python scripts/prepare_dataset.py --config configs/data/real_v03.yaml --dry-run
```

准备真实数据。若 `data/raw/PapalexiSatija2021_eccite_arrayed_RNA.h5ad` 已存在，会校验 md5；若不存在，配置允许从 Zenodo 下载约 52.3 MB 文件：

```powershell
python scripts/prepare_dataset.py --config configs/data/real_v03.yaml
```

运行真实数据 baseline smoke benchmark：

```powershell
python scripts/run_real_baseline.py --config configs/experiment/real_v03_baselines.yaml
```

输出会写入：

```text
outputs/runs/v0.3-real-benchmark-baselines/scperturb_papalexi_2021_arrayed_rna/<timestamp>/
```

schema report 也会镜像写入：

```text
outputs/data_reports/scperturb_papalexi_2021_arrayed_rna/<timestamp>/schema_report.md
```

原始数据和运行产物都不提交到 git。

## v0.4 Quickstart

运行重复真实 baseline 评测：

```powershell
python scripts/run_repeated_baselines.py --config configs/experiment/real_v04_repeated_baselines.yaml
```

输出位置：

```text
outputs/runs/v0.4-real-baseline-strengthening/scperturb_papalexi_2021_arrayed_rna/<timestamp>/
```

运行小型预处理敏感性审计：

```powershell
python scripts/run_sensitivity.py --config configs/experiment/real_v04_sensitivity.yaml
```

输出位置：

```text
outputs/runs/v0.4-real-baseline-sensitivity/scperturb_papalexi_2021_arrayed_rna/<timestamp>/
```

公开 benchmark 对齐状态记录在 [docs/PUBLIC_BENCHMARK_ALIGNMENT_V04.md](docs/PUBLIC_BENCHMARK_ALIGNMENT_V04.md)。当前结论是：v0.4 仍是项目自定义真实数据 baseline，不是 public leaderboard 或论文 split。

## v0.5 Quickstart

运行 synthetic multi-cell-type lineage sanity benchmark：

```powershell
python scripts/run_lineage_prior.py --config configs/experiment/synthetic_v05_lineage.yaml
```

输出位置：

```text
outputs/runs/v0.5-first-lineage-prior/synthetic_lineage/<timestamp>/
```

运行 Papalexi 真实数据兼容/no-op 检查：

```powershell
python scripts/run_lineage_prior.py --config configs/experiment/real_v05_lineage_compatibility.yaml
```

输出位置：

```text
outputs/runs/v0.5-first-lineage-prior/scperturb_papalexi_2021_arrayed_rna/<timestamp>/
```

v0.5 相关说明：

- 设计边界：[docs/V05_LINEAGE_PRIOR_DESIGN.md](docs/V05_LINEAGE_PRIOR_DESIGN.md)。
- 未来真实多细胞数据集要求：[docs/V05_MULTICELL_DATASET_REQUIREMENTS.md](docs/V05_MULTICELL_DATASET_REQUIREMENTS.md)。
- 真实多细胞候选侦察：[docs/V05_REAL_MULTICELL_DATASET_SCOUTING.md](docs/V05_REAL_MULTICELL_DATASET_SCOUTING.md)。
- Papalexi 只有一个配置内 cell type/cell line，不能验证谱系泛化。

## v0.6 Quickstart

先查看 Kang 2018 PBMC IFN-beta 数据准备计划：

```powershell
python scripts/prepare_dataset.py --config configs/data/real_multicell_v06.yaml --dry-run
```

准备真实 multi-cell-type 数据。配置文件记录 Figshare URL、38,356,412 bytes 文件体量和 md5：

```powershell
python scripts/prepare_dataset.py --config configs/data/real_multicell_v06.yaml
```

运行 v0.6 real multi-cell-type lineage benchmark：

```powershell
python scripts/run_lineage_real_benchmark.py --config configs/experiment/real_v06_multicell_lineage.yaml
```

输出位置：

```text
outputs/runs/v0.6-real-multicell-lineage-benchmark/kang_2018_pbmc_ifnb/<timestamp>/
```

可选运行预设 tau sensitivity audit：

```powershell
python scripts/run_lineage_real_benchmark.py --config configs/experiment/real_v06_lineage_tau_audit.yaml
```

输出位置：

```text
outputs/runs/v0.6-real-multicell-lineage-tau-audit/kang_2018_pbmc_ifnb/<timestamp>/
```

v0.6 相关说明：

- 数据选择：[docs/V06_REAL_MULTICELL_DATASET_SELECTION.md](docs/V06_REAL_MULTICELL_DATASET_SELECTION.md)。
- benchmark 设计：[docs/V06_LINEAGE_REAL_BENCHMARK_DESIGN.md](docs/V06_LINEAGE_REAL_BENCHMARK_DESIGN.md)。
- 主要输出：`outputs/runs/v0.6-real-multicell-lineage-benchmark/kang_2018_pbmc_ifnb/20260623T092131Z/`。
- tau audit 输出：`outputs/runs/v0.6-real-multicell-lineage-tau-audit/kang_2018_pbmc_ifnb/20260623T092131Z/`。

## v0.7 Quickstart

v0.7 adds a non-neural gene-prior substrate and residual-correction baseline. It does not implement neural EvoPrior and does not establish real evolutionary-prior benefit.

Run the synthetic gene-prior sanity benchmark:

```powershell
python scripts/run_gene_prior.py --config configs/experiment/synthetic_v07_gene_prior.yaml
```

Output pattern:

```text
outputs/runs/v0.7-gene-evolutionary-prior/synthetic_gene_prior/<timestamp>/
```

Run the Kang gene-prior compatibility benchmark:

```powershell
python scripts/prepare_gene_prior.py --config configs/priors/gene_prior_v07.yaml --dry-run
python scripts/run_gene_prior.py --config configs/experiment/real_v07_kang_gene_prior.yaml
```

Output pattern:

```text
outputs/runs/v0.7-gene-evolutionary-prior/kang_2018_pbmc_ifnb/<timestamp>/
```

v0.7 claim boundary:

- synthetic results validate plumbing and ablation logic only;
- Kang currently uses an engineering-only synthetic/placeholder gene prior;
- Kang v0.7 is compatibility-only and does not test real evolutionary-prior benefit;
- no SOTA, public leaderboard, biological-discovery, causal evolutionary, pathway-prior, or neural EvoPrior claim.

## v0.8 Quickstart

v0.8 replaces the v0.7 Kang placeholder prior with a real HGNC functional/gene-metadata source. This is not a real evolutionary/conservation-prior test because no orthology, conservation score, or gene-age source is configured.

Prepare the real source:

```powershell
python scripts/prepare_gene_prior.py --config configs/priors/gene_prior_real_v08.yaml --dry-run
python scripts/prepare_gene_prior.py --config configs/priors/gene_prior_real_v08.yaml
```

Run the Kang HGNC metadata-prior ablation:

```powershell
python scripts/run_gene_prior.py --config configs/experiment/real_v08_kang_real_gene_prior.yaml
```

Output pattern:

```text
outputs/runs/v0.8-real-versioned-gene-prior-source/kang_2018_pbmc_ifnb/<timestamp>/
outputs/data_reports/kang_2018_pbmc_ifnb/<timestamp>/real_gene_prior_v08_coverage_report.md
```

v0.8 claim boundary:

- source mode is `download_hgnc`;
- source kind is `real_functional_gene_metadata`;
- Kang v0.8 is preliminary and dataset/split-specific;
- no real evolutionary/conservation-prior benefit, SOTA, biological-discovery, causal evolutionary, pathway-prior, or neural EvoPrior claim.

## v0.9 Quickstart

v0.9 adds `EvoPriorAdditiveModel`, a transparent non-neural additive model that combines global, perturbation, lineage, and optional gene-metadata residual components. It is not a neural EvoPrior model.

Run the synthetic integrated sanity benchmark:

```powershell
python scripts/run_evoprior_additive.py --config configs/experiment/synthetic_v09_integrated_evoprior.yaml
```

Run the Kang integrated additive benchmark:

```powershell
python scripts/run_evoprior_additive.py --config configs/experiment/real_v09_kang_evoprior_additive.yaml
```

Output pattern:

```text
outputs/runs/v0.9-integrated-evoprior-additive/<dataset_id>/<timestamp>/
```

v0.9 claim boundary:

- integrated additive model is non-neural and audit-friendly;
- Kang results are preliminary and project-split-specific;
- HGNC metadata is not a true evolutionary/conservation prior;
- no SOTA, public-leaderboard, biological-discovery, causal evolutionary, pathway-prior, or neural EvoPrior claim.

## v0.10 Quickstart

v0.10 adds benchmark evidence alignment. It collects existing v0.6-v0.9 run artifacts into unified JSON/CSV/Markdown evidence tables. It does not train new models or import external benchmark data.

Run synthetic evidence alignment:

```powershell
python scripts/run_benchmark_alignment.py --config configs/experiment/v10_benchmark_alignment_synthetic.yaml
```

Run Kang evidence alignment:

```powershell
python scripts/run_benchmark_alignment.py --config configs/experiment/v10_benchmark_alignment_kang.yaml
```

Output pattern:

```text
outputs/runs/v0.10-public-benchmark-alignment/<dataset_id>/<timestamp>/
```

v0.10 claim boundary:

- strongest current evidence: v0.9 integrated additive improves over `lineage_shrinkage` on the project Kang split;
- weak evidence: HGNC gene-prior additive variant does not beat the no-gene-prior additive control on MAE;
- component audit shows the gene-prior component is inspectable and not collapsed, but mostly lineage-dominated;
- public external benchmark alignment remains blocked until external splits/data are imported and versioned.

## v0.11 Quickstart

v0.11 adds manifest-driven external public benchmark ingestion planning. It registers benchmark metadata, validates registry records, builds adapter-level ingestion plans, and writes auditable JSON/CSV/Markdown planning artifacts. It does not download large external data, commit raw data, train models, or produce performance evidence.

Run the ingestion planner:

```powershell
python scripts/plan_public_benchmark_ingestion.py --config configs/experiment/v11_public_benchmark_ingestion_plan.yaml
```

Output pattern:

```text
outputs/runs/v0.11-external-public-benchmark-ingestion/<timestamp>/
```

v0.11 claim boundary:

- metadata registration is not benchmark evidence;
- successful ingestion planning is not performance evidence;
- public benchmark claims remain blocked until local data ingestion, split validation, model runs, and v0.10 evidence records exist;
- v0.9/v0.10 claim boundaries remain unchanged.

## 数据政策

- 不提交大型原始数据。
- `data/raw/`、`data/interim/`、`data/processed/` 仅保留 `.gitkeep`。
- 所有下载、预处理和切分必须记录数据版本、checksum、split ID 和配置。
- 任何模型声称都必须能追溯到 `docs/EXPERIMENT_LEDGER.md` 中的实验 ID。

## 下一安全里程碑

v0.12 可以考虑 local public benchmark smoke run only if a small legally usable local fixture or already prepared local dataset exists. Otherwise, continue external data acquisition documentation and do not start neural modeling.
