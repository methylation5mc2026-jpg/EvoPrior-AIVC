# EvoPrior-AIVC

EvoPrior-AIVC 是一个面向单细胞扰动响应预测的研究工程项目。目标不是做泛泛的“AI for biology”演示，而是在明确公开数据集、固定切分、统一评测脚本和可复现实验记录之上，检验“细胞谱系先验、基因演化/保守性先验、通路/网络先验是否能提升外推预测”这个窄而严肃的问题。

当前仓库处于 v0.2-data-pipeline-and-baselines 阶段：已经建立 synthetic AnnData 数据管线、pseudobulk 聚合、四个基础 baseline、固定指标评测、泄漏检查和端到端 synthetic smoke runner。不要在这个阶段实现大型神经网络或声称生物学性能。

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

## 数据政策

- 不提交大型原始数据。
- `data/raw/`、`data/interim/`、`data/processed/` 仅保留 `.gitkeep`。
- 所有下载、预处理和切分必须记录数据版本、checksum、split ID 和配置。
- 任何模型声称都必须能追溯到 `docs/EXPERIMENT_LEDGER.md` 中的实验 ID。

## 下一安全里程碑

v0.3 的下一步是接入一个真实公开扰动数据集，并在不改变评测脚本语义的前提下复现实用 baseline：

1. 选择一个可访问的公开扰动数据集。
2. 写入下载/校验/AnnData schema 检查。
3. 实现 pseudobulk 聚合。
4. 实现 no-change、mean、additive、ridge 基线。
5. 用固定评测脚本生成 baseline report。

在真实数据集 baseline 闭环完成前，不实现 EvoPrior 神经模块。
