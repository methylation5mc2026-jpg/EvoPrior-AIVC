# EvoPrior-AIVC

![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue)
![Tests](https://img.shields.io/badge/tests-164%20passed-brightgreen)
![Release](https://img.shields.io/badge/release-v0.24%20publish%20ready-informational)
![License](https://img.shields.io/badge/license-see%20LICENSE-lightgrey)

Reproducible single-cell perturbation-response prediction benchmark pipeline with structured priors and a validated residual baseline on a GEARS-compatible Norman split.

## Key Result

Public Norman/scPerturb H5AD, md5 `c870e6967d91c017d9da827bab183cd6`; fixed internal GEARS-compatible seen0/seen1/seen2/random_combo split; metrics are internal compatible metrics, not official GEARS leaderboard metrics.

| milestone/model | MAE | MSE | Pearson | Spearman | status |
| --- | ---: | ---: | ---: | ---: | --- |
| v0.14 `weighted_combo_additive` | 0.5660 | 6.6759 | 0.7599 | 0.6390 | transparent additive baseline |
| v0.15 fast MLP/PCA | 0.5877 | 7.5517 | 0.7134 | 0.6317 | lightweight trained baseline |
| v0.17 residual baseline | 0.430778 | 3.668870 | 0.869224 | 0.784976 | five-seed validated baseline |

Claim boundary: this is a strong internal GEARS-compatible Norman result under a documented split and metric script. It is not official GEARS, not leaderboard-comparable, not SOTA, and not biological discovery.

## Quick Links

- Model card: `docs/V18_RELEASE_MODEL_CARD.md`
- Benchmark card: `docs/V18_BENCHMARK_CARD.md`
- Reproducibility runbook: `docs/V18_REPRODUCIBILITY_RUNBOOK.md`
- External result card: `docs/V17_EXTERNAL_RESULT_CARD.md`
- Public data guide: `docs/V21_PUBLIC_DATA_ACQUISITION_GUIDE.md`
- Final release notes: `docs/V22_GITHUB_RELEASE_NOTES_FINAL.md`
- Public demo guide: `docs/V22_PUBLIC_DEMO_GUIDE.md`
- Repo profile copy: `docs/V22_GITHUB_REPO_PROFILE.md`
- GitHub publish guide: `docs/V23_GITHUB_PUBLISH_GUIDE.md`
- GitHub release body: `docs/V23_GITHUB_RELEASE_BODY.md`
- Project page assets: `docs/V23_PROJECT_PAGE_ASSETS.md`
- Mentor review brief: `docs/V23_MENTOR_REVIEW_BRIEF.md`
- Showcase index: `docs/V23_SHOWCASE_INDEX.md`
- Final publication checklist: `docs/V23_FINAL_PUBLICATION_CHECKLIST.md`
- v0.24 publish status: `docs/V24_GITHUB_PUBLISH_STATUS.md`
- v0.24 release draft: `docs/V24_GITHUB_RELEASE_DRAFT.md`
- v0.24 website assets: `docs/V24_WEBSITE_INTEGRATION_ASSETS.md`
- v0.25 publish execution log: `docs/V25_GITHUB_PUBLISH_EXECUTION_LOG.md`
- v0.25 final link package: `docs/V25_FINAL_LINK_PACKAGE.md`
- v0.25 mentor email snippet: `docs/V25_MENTOR_EMAIL_SNIPPET.md`
- v0.26 main/release verification: `docs/V26_MAIN_BRANCH_AND_RELEASE_VERIFICATION.md`
- v0.26 final share links: `docs/V26_FINAL_SHARE_LINKS.md`
- v0.26 mentor-ready message: `docs/V26_MENTOR_READY_MESSAGE.md`

## Quickstart

```powershell
python -m pip install -e ".[dev]"
python -m pytest -p no:cacheprovider --basetemp .tmp_pytest_local
python scripts/run_release_smoke.py --config configs/experiment/release_smoke_v019.yaml
python scripts/run_norman_residual_multiseed.py --config configs/experiment/gears_norman_v017_multiseed_residual.yaml
```

## No-Data Review

This path is intended for GitHub reviewers without raw Norman data:

```powershell
python -m pip install -e ".[dev]"
python -m pytest -p no:cacheprovider --basetemp .tmp_pytest_local tests/test_release_smoke_config.py tests/test_release_artifact_manifest.py tests/test_official_gears_diagnostics.py tests/test_ci_workflow_static.py
python scripts/check_ci_workflow.py --workflow .github/workflows/ci.yml
python scripts/run_release_smoke.py --config configs/experiment/release_smoke_v019.yaml
python scripts/make_release_bundle.py --config configs/release/v024_release_bundle.yaml
python scripts/check_release_artifacts.py
```

Then read `docs/V18_RELEASE_MODEL_CARD.md`, `docs/V18_BENCHMARK_CARD.md`, `docs/V22_GITHUB_RELEASE_NOTES_FINAL.md`, and `docs/V22_PUBLIC_DEMO_GUIDE.md`.

Latest public review bundle is refreshed by v0.24 under `outputs/release/v0.24/<timestamp>/`.

v0.24 publication assets are documentation-only materials for GitHub publication, GitHub Release drafting, personal website integration, public link audit, and mentor review. They do not push to GitHub, update a website, or change the benchmark result.

v0.25 pushed the complete project package to `feat/github-publish-execution-v025` at `https://github.com/methylation5mc2026-jpg/EvoPrior-AIVC`. v0.26 records that the repository root still defaults to `main`, which currently has only the minimal bootstrap files; use the feature-branch URL until `main` is merged.

## With-Data Reproduction

Place `NormanWeissman2019_filtered.h5ad` at `data/raw/NormanWeissman2019_filtered.h5ad`. Expected md5: `c870e6967d91c017d9da827bab183cd6`.

```powershell
python scripts/prepare_gears_norman.py --config configs/data/gears_norman_v013.yaml --dry-run
python scripts/run_norman_residual_multiseed.py --config configs/experiment/gears_norman_v017_multiseed_residual.yaml
python scripts/check_release_artifacts.py
```

## Review Map

- Model card: `docs/V18_RELEASE_MODEL_CARD.md`
- Benchmark card: `docs/V18_BENCHMARK_CARD.md`
- Reproducibility runbook: `docs/V18_REPRODUCIBILITY_RUNBOOK.md`
- External review index: `docs/V18_EXTERNAL_REVIEW_INDEX.md`
- Final release notes: `docs/V22_GITHUB_RELEASE_NOTES_FINAL.md`
- Public demo guide: `docs/V22_PUBLIC_DEMO_GUIDE.md`
- Public final check: `docs/V22_PUBLIC_GITHUB_FINAL_CHECK.md`
- Sanitization report: `docs/V22_REPO_SANITIZATION_REPORT.md`
- Public repo checklist: `docs/V19_PUBLIC_REPO_REVIEW_CHECKLIST.md`
- GEARS unblock plan: `docs/V19_OFFICIAL_GEARS_UNBLOCK_PLAN.md`
- Portfolio summary: `docs/V19_APPLICATION_PORTFOLIO_SUMMARY.md`
- v0.20 release plan: `docs/V20_GITHUB_RELEASE_PLAN.md`
- v0.20 CI docs: `docs/V20_GITHUB_ACTIONS_CI.md`
- v0.20 Docker/WSL GEARS route: `docs/V20_OFFICIAL_GEARS_DOCKER_ENV.md`
- v0.20 release checklist: `docs/V20_RELEASE_CHECKLIST.md`
- v0.21 release candidate plan: `docs/V21_RELEASE_CANDIDATE_PLAN.md`
- v0.21 public data guide: `docs/V21_PUBLIC_DATA_ACQUISITION_GUIDE.md`
- v0.21 release notes: `docs/V21_GITHUB_RELEASE_NOTES.md`
- v0.21 CI validation: `docs/V21_CI_VALIDATION_REPORT.md`
- v0.21 Docker GEARS test report: `docs/V21_DOCKER_GEARS_TEST_REPORT.md`
- v0.23 GitHub publish guide: `docs/V23_GITHUB_PUBLISH_GUIDE.md`
- v0.23 GitHub release body: `docs/V23_GITHUB_RELEASE_BODY.md`
- v0.23 project page assets: `docs/V23_PROJECT_PAGE_ASSETS.md`
- v0.23 mentor review brief: `docs/V23_MENTOR_REVIEW_BRIEF.md`
- v0.23 showcase index: `docs/V23_SHOWCASE_INDEX.md`
- v0.23 final publication checklist: `docs/V23_FINAL_PUBLICATION_CHECKLIST.md`
- v0.24 publish status: `docs/V24_GITHUB_PUBLISH_STATUS.md`
- v0.24 publish commands: `docs/V24_GITHUB_PUBLISH_COMMANDS.md`
- v0.24 GitHub release draft: `docs/V24_GITHUB_RELEASE_DRAFT.md`
- v0.24 website integration assets: `docs/V24_WEBSITE_INTEGRATION_ASSETS.md`
- v0.24 public link audit: `docs/V24_PUBLIC_LINK_AUDIT.md`
- v0.24 final presentation summary: `docs/V24_FINAL_PRESENTATION_SUMMARY.md`
- v0.25 GitHub publish execution log: `docs/V25_GITHUB_PUBLISH_EXECUTION_LOG.md`
- v0.25 final publish commands: `docs/V25_GITHUB_FINAL_PUBLISH_COMMANDS.md`
- v0.25 final link package: `docs/V25_FINAL_LINK_PACKAGE.md`
- v0.25 mentor email snippet: `docs/V25_MENTOR_EMAIL_SNIPPET.md`
- v0.25 post-publish verification: `docs/V25_POST_PUBLISH_VERIFICATION.md`
- v0.26 main/default branch verification: `docs/V26_MAIN_BRANCH_AND_RELEASE_VERIFICATION.md`
- v0.26 release execution log: `docs/V26_GITHUB_RELEASE_EXECUTION_LOG.md`
- v0.26 public final check: `docs/V26_PUBLIC_REPO_FINAL_CHECK.md`
- v0.26 final share links: `docs/V26_FINAL_SHARE_LINKS.md`
- v0.26 mentor-ready message: `docs/V26_MENTOR_READY_MESSAGE.md`

## Data And GEARS Status

Raw data is not committed. The expected Norman file is `data/raw/NormanWeissman2019_filtered.h5ad`; use `python scripts/prepare_gears_norman.py --config configs/data/gears_norman_v013.yaml --dry-run` to verify access instructions.

Official GEARS status: `import_ok_run_blocked`. The isolated `.venv_gears` environment imports the dependency stack, but the repository wrapper is still feasibility-only and does not train/evaluate official GEARS.

v0.20 adds a Docker/WSL environment route at `docs/V20_OFFICIAL_GEARS_DOCKER_ENV.md` and `docker/Dockerfile.gears`. This is an unblock path, not a claimed official GEARS result.

v0.21 Docker status: `unavailable_docker`. Local Docker was not available on PATH, so no Docker image build, container import check, official GEARS training, official split import, or official metric output is claimed.

## v0.19 Review Smoke

v0.19 adds public-repo metadata, release smoke checks, an official GEARS diagnostic, and an artifact manifest. It does not change the v0.17 model, split, metrics, or claim boundary.

```powershell
python scripts/run_release_smoke.py --config configs/experiment/release_smoke_v019.yaml
python scripts/diagnose_official_gears.py
python scripts/check_release_artifacts.py
```

Latest local smoke output: `outputs/runs/v0.19-release-smoke/20260625T223712Z/`.
Latest diagnostic output: `outputs/runs/v0.19-official-gears-diagnostics/20260625T223710Z/`.
Latest v0.20 smoke output: `outputs/runs/v0.19-release-smoke/20260625T230440Z/`.
Latest v0.20 diagnostic output: `outputs/runs/v0.20-official-gears-diagnostics/20260625T230451Z/`.

## v0.18 Validated Norman Baseline Release Quickstart

v0.18 packages the validated Norman residual baseline for external review and records a final official GEARS feasibility attempt. The official dependency stack imports inside `.venv_gears`, but the repository wrapper is still feasibility-only and does not produce official GEARS metrics.

Run:

```powershell
python scripts/run_norman_residual_multiseed.py --config configs/experiment/gears_norman_v017_multiseed_residual.yaml
```

Release docs:

- model card: `docs/V18_RELEASE_MODEL_CARD.md`;
- benchmark card: `docs/V18_BENCHMARK_CARD.md`;
- reproducibility runbook: `docs/V18_REPRODUCIBILITY_RUNBOOK.md`;
- external review index: `docs/V18_EXTERNAL_REVIEW_INDEX.md`;
- release manifest: `reports/v0.18_release_manifest.md`.

Claim boundary: internal GEARS-compatible Norman split only; not official GEARS, not leaderboard-comparable, and not SOTA.

## v0.17 Validated Norman Residual Baseline Quickstart

v0.17 validates the v0.16 residual baseline on the fixed public Norman/scPerturb GEARS-compatible internal split with five seeds, ablations, negative controls, leakage stress checks, and repeat-level confidence intervals. It is not official GEARS, not leaderboard-comparable, and not SOTA.

Run:

```powershell
python scripts/run_norman_residual_multiseed.py --config configs/experiment/gears_norman_v017_multiseed_residual.yaml
```

Latest output:

```text
outputs/runs/v0.17-norman-validated-residual-baseline/gears_norman_scperturb_v013/20260625T100322Z/
```

Main result:

- seeds: `0, 1, 2, 3, 4`;
- dataset md5: `c870e6967d91c017d9da827bab183cd6`;
- primary model: `weighted_pca_ridge_s075_a10`;
- test MAE/MSE/Pearson/Spearman mean: `0.4308 / 3.6689 / 0.8692 / 0.7850`;
- leakage stress: all critical checks passed;
- external card: `docs/V17_EXTERNAL_RESULT_CARD.md`.

## v0.16 Norman Residual Sprint Quickstart

v0.16 adds a validation-selected residual correction sprint on the public Norman/scPerturb GEARS-compatible internal split. It improves the project-owned baseline result, but it is still not official GEARS, not leaderboard-comparable, and not SOTA.

Run:

```powershell
python scripts/run_norman_residual_sprint.py --config configs/experiment/gears_norman_v016_residual_sweep.yaml
```

Latest output:

```text
outputs/runs/v0.16-model-improvement-sprint/gears_norman_scperturb_v013/20260625T031612Z/
```

Main result:

- selected model: `weighted_pca_ridge_s075_a10`;
- test MAE/MSE/Pearson/Spearman: `0.4308 / 3.6689 / 0.8692 / 0.7850`;
- v0.14 `weighted_combo_additive`: `0.5660 / 6.6759 / 0.7599 / 0.6390`;
- official GEARS status: dependencies import in `.venv_gears`, but the repo wrapper does not yet produce official GEARS metrics.

## v0.15 Fast Neural Norman Quickstart

v0.15 adds a fast neural-style Norman baseline using sklearn `MLPRegressor` over PCA-compressed delta-expression targets. PyTorch and official GEARS dependencies remain unavailable in the current environment, so this is not an official GEARS model reproduction.

Run:

```powershell
python scripts/run_fast_neural_norman.py --config configs/experiment/gears_norman_v015_fast_neural.yaml
```

Latest output:

```text
outputs/runs/v0.15-fast-neural-norman-baseline/gears_norman_scperturb_v013/20260625T023033Z/
```

Claim boundary:

- public Norman/scPerturb H5AD, md5 `c870e6967d91c017d9da827bab183cd6`;
- v0.14 internal GEARS-compatible split with seen0/seen1/seen2/random_combo classes;
- `fast_combo_mlp_pca_sklearn` was trained with seeds 1510, 1511, and 1512;
- test MAE mean was 0.5877 and Pearson delta mean was 0.7134 across the three neural seeds;
- v0.14 `weighted_combo_additive` remains stronger on test MAE/MSE under this exact split;
- no official GEARS, leaderboard, SOTA, biological-discovery, or general neural-superiority claim.

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

## v0.12 Quickstart

v0.12 runs the first public-data, benchmark-compatible baseline round. The selected dataset is the Papalexi/Satija scPerturb H5AD already used by earlier plumbing work, now with a dedicated v0.12 data config, split report, evidence artifacts, and explicit claim boundary.

Prepare or dry-run the public benchmark data:

```powershell
python scripts/prepare_public_benchmark.py --config configs/data/public_benchmark_v012.yaml --dry-run
python scripts/prepare_public_benchmark.py --config configs/data/public_benchmark_v012.yaml
```

Run the v0.12 baseline:

```powershell
python scripts/run_public_benchmark_baseline.py --config configs/experiment/public_benchmark_v012_baseline.yaml
```

Output pattern:

```text
outputs/runs/v0.12-public-benchmark-baseline-run/scperturb_papalexi_2021_arrayed_rna_v012/<timestamp>/
outputs/data_reports/scperturb_papalexi_2021_arrayed_rna_v012/<timestamp>/
```

v0.12 claim boundary:

- public scPerturb-compatible data, locked checksum, custom leave-one-perturbation split, and internal compatible metrics;
- not official leaderboard aligned;
- test metrics are underpowered in the current local split;
- no SOTA, public leaderboard, biological discovery, neural EvoPrior, or general EvoPrior superiority claim.

## v0.13 Quickstart

v0.13 runs a GEARS-compatible internal Norman combinatorial Perturb-seq baseline on the public scPerturb H5AD. It is closer to the perturbation-prediction benchmark literature than v0.12, but it is still not an official GEARS leaderboard result because the exact official GEARS split and metric package are not imported.

Prepare or dry-run the Norman data:

```powershell
python scripts/prepare_gears_norman.py --config configs/data/gears_norman_v013.yaml --dry-run
python scripts/prepare_gears_norman.py --config configs/data/gears_norman_v013.yaml
```

Run the v0.13 baseline:

```powershell
python scripts/run_gears_norman_baseline.py --config configs/experiment/gears_norman_v013_baseline.yaml
```

Output pattern:

```text
outputs/runs/v0.13-gears-norman-baseline/gears_norman_scperturb_v013/<timestamp>/
outputs/data_reports/gears_norman_scperturb_v013/<timestamp>/
```

Latest audited local output:

```text
outputs/runs/v0.13-gears-norman-baseline/gears_norman_scperturb_v013/20260625T002742Z/
```

v0.13 claim boundary:

- public scPerturb Norman H5AD with md5 `c870e6967d91c017d9da827bab183cd6`;
- GEARS-compatible internal seen0/seen1/seen2 combo split, not official GEARS split;
- internal compatible metrics: MAE, MSE, Pearson delta, Spearman logFC, DE20/DE50 recovery;
- strongest implemented baseline is `single_effect_additive_combo`, test MAE 0.5491 and Pearson delta 0.7538 under this exact split;
- no SOTA, leaderboard, official GEARS, neural GEARS, biological-discovery, or general EvoPrior superiority claim.

## v0.14 Quickstart

v0.14 strengthens the Norman package with an official GEARS wrapper feasibility layer, an explicit `random_combo` split category, and a fast `weighted_combo_additive` baseline. The official wrapper is blocked in the current environment because `cell-gears`, `gears`, `torch`, and `torch_geometric` are unavailable and `pip install cell-gears` fails with `WinError 5`.

Run the aligned baseline:

```powershell
python scripts/run_gears_norman_baseline.py --config configs/experiment/gears_norman_v014_aligned_baseline.yaml
```

Run the official wrapper dry-run/blocker:

```powershell
python scripts/run_official_gears_wrapper.py --config configs/experiment/gears_norman_v014_official_wrapper.yaml --dry-run
```

Latest v0.14 outputs:

```text
outputs/runs/v0.14-gears-aligned-baseline/gears_norman_scperturb_v013/20260625T014719Z/
outputs/runs/v0.14-official-gears-wrapper-blocked/gears_norman_scperturb_v013/20260625T014710Z/
```

v0.14 claim boundary:

- GEARS-compatible/internal alignment is tightened, but official GEARS remains blocked;
- `weighted_combo_additive` has the best test MAE/MSE in this run, while `single_effect_additive_combo` has slightly stronger Pearson/Spearman;
- no official GEARS, leaderboard, SOTA, neural GEARS, or biological-discovery claim.

## 数据政策

- 不提交大型原始数据。
- `data/raw/`、`data/interim/`、`data/processed/` 仅保留 `.gitkeep`。
- 所有下载、预处理和切分必须记录数据版本、checksum、split ID 和配置。
- 任何模型声称都必须能追溯到 `docs/EXPERIMENT_LEDGER.md` 中的实验 ID。

## 下一安全里程碑

v0.12 可以考虑 local public benchmark smoke run only if a small legally usable local fixture or already prepared local dataset exists. Otherwise, continue external data acquisition documentation and do not start neural modeling.
