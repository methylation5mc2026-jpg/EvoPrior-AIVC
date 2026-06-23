# EvoPrior-AIVC

EvoPrior-AIVC 是一个面向单细胞扰动响应预测的研究工程项目。目标不是做泛泛的“AI for biology”演示，而是在明确公开数据集、固定切分、统一评测脚本和可复现实验记录之上，检验“细胞谱系先验、基因演化/保守性先验、通路/网络先验是否能提升外推预测”这个窄而严肃的问题。

当前仓库已推进到 v0.5-first-lineage-prior-module：在 v0.4 强化基线层之上，新增细胞谱系树/映射/特征工具、synthetic multi-cell-type lineage 数据生成器、一个非神经 `LineageShrinkageBaseline`，以及 synthetic lineage sanity benchmark。v0.5 只证明谱系先验基础设施和 synthetic 逻辑验证跑通；Papalexi 真实数据仅做兼容/no-op 检查，不支撑真实生物谱系有效性声称。

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

## 数据政策

- 不提交大型原始数据。
- `data/raw/`、`data/interim/`、`data/processed/` 仅保留 `.gitkeep`。
- 所有下载、预处理和切分必须记录数据版本、checksum、split ID 和配置。
- 任何模型声称都必须能追溯到 `docs/EXPERIMENT_LEDGER.md` 中的实验 ID。

## 下一安全里程碑

v0.6 的下一步应选择一个真实 multi-cell-type perturbation 数据集，并在固定 split/metric 下比较 v0.4 classical baselines 与 v0.5 lineage-aware baseline：

1. 先锁定数据版本、下载体量、checksum、许可和 schema mapping。
2. 优先选择支持 held-out cell type、held-out lineage 或 held-out donor/context 的数据。
3. 保留 v0.4 baseline 对照和 v0.5 lineage ablation，不做 SOTA 声称。
4. 若真实数据只有 cell line 而非发育谱系，只能称为 context/cell-line transfer，不写成生物谱系验证。
5. 在真实多细胞结果前，不把 synthetic lineage 结果写成真实生物有效。
