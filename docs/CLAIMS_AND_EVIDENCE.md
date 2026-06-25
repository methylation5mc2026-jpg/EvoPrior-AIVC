# 声称与证据

## 原则

本项目所有科学和性能声称必须指向实验 ID。没有实验 ID 的内容只能作为计划、假设或未来工作。

## 已证明

- `v0.2-synthetic-baseline-smoke`: 仓库可以运行完整 synthetic perturbation baseline loop，包括 schema validation、pseudobulk aggregation、random/heldout split、四个 baseline、metrics JSON、prediction CSV、split assignment 和 markdown report。
- `v0.2-synthetic-baseline-smoke`: 在 synthetic smoke test 中，四个 baseline 都能产生有限预测和指标。这是工程级证据，不是生物学证据。
- `v0.3-real-benchmark-baselines`: 项目支持一个真实公开 perturbation H5AD 数据集通过 canonical schema。证据：`scperturb_papalexi_2021_arrayed_rna` adapter schema report。
- `v0.3-real-benchmark-baselines`: baseline evaluation loop 可以在真实数据上端到端运行，并生成 metrics、predictions、split manifest、schema report、failure cases 和 markdown report。
- `v0.3-real-benchmark-baselines`: selected held-out perturbation split 的 leakage check 通过；`pdl1` 不出现在训练/验证 split 中。
- `v0.4-real-baseline-strengthening`: repeated real-data baseline evaluation works and writes per-run metrics, metric summaries, confidence intervals, retrieval summaries, DE summaries, skipped perturbations, and a v0.4 report.
- `v0.4-real-baseline-strengthening`: perturbation-level retrieval metrics and DE recovery metrics are implemented with unit tests.
- `v0.4-real-baseline-strengthening`: preprocessing sensitivity audit runs over a compact matrix and reports metric fragility.
- `docs/PUBLIC_BENCHMARK_ALIGNMENT_V04.md`: current v0.4 setup has been audited and is explicitly not public-benchmark-aligned.
- `v0.5-synthetic-lineage-prior`: lineage tree infrastructure, cell-type-to-lineage mapping, lineage distance/features, synthetic multi-cell-type lineage data generation, and one non-neural lineage-aware baseline are implemented with tests.
- `v0.5-synthetic-lineage-prior`: on a known synthetic lineage-structured generator, `lineage_shrinkage` can be evaluated against v0.4-style classical baselines under held-out cell-type splits. This is synthetic logic validation only.
- `v0.5-papalexi-lineage-compatibility`: the lineage baseline runs safely on the existing Papalexi real-data plumbing in compatibility/no-op mode, and the report records that lineage signal is not identifiable with one configured cell type.
- `v0.6-real-multicell-lineage-benchmark`: a real multi-cell-type PBMC IFN-beta benchmark is implemented on `kang_2018_pbmc_ifnb` with documented schema mapping, coarse lineage mapping, held-out cell-type splits, leakage checks, v0.4 baselines, and v0.5 `lineage_shrinkage`.
- `v0.6-real-multicell-lineage-benchmark`: on this dataset and project-defined held-out cell-type suite, `lineage_shrinkage` improves mean test MAE/MSE/Pearson/Spearman over the configured v0.4 classical baselines. Output: `outputs/runs/v0.6-real-multicell-lineage-benchmark/kang_2018_pbmc_ifnb/20260623T092131Z/`.
- `v0.6-real-multicell-lineage-tau-audit`: pre-specified tau values were audited as sensitivity only. Output: `outputs/runs/v0.6-real-multicell-lineage-tau-audit/kang_2018_pbmc_ifnb/20260623T092131Z/`.
- `v0.7-synthetic-gene-prior`: `GenePriorTable`, synthetic gene-prior data generation, `GenePriorCorrectionBaseline`, prior audit, shuffled negative control, and v0.7 runner plumbing are implemented and tested. Output: `outputs/runs/v0.7-gene-evolutionary-prior/synthetic_gene_prior/20260624T004215Z/`.
- `v0.7-kang-gene-prior-compatibility`: Kang gene-prior feature mapping, coverage, correction runner, and report generation run end-to-end with an engineering-only synthetic/placeholder prior. Output: `outputs/runs/v0.7-gene-evolutionary-prior/kang_2018_pbmc_ifnb/20260624T004226Z/`.
- `v0.8-kang-real-gene-metadata-prior`: HGNC complete-set source preparation, manifest checksums, feature construction, Kang coverage reporting, and Kang ablation run end-to-end with a real functional/gene-metadata source. Output: `outputs/runs/v0.8-real-versioned-gene-prior-source/kang_2018_pbmc_ifnb/20260624T010126Z/`.
- `v0.9-synthetic-integrated-evoprior-additive`: `EvoPriorAdditiveModel`, component audit, negative controls, and integrated additive runner run end-to-end on synthetic data. Output: `outputs/runs/v0.9-integrated-evoprior-additive/synthetic_integrated/20260624T015634Z/`.
- `v0.9-kang-evoprior-additive`: a transparent non-neural additive model runs on the Kang held-out-cell-type suite and improves over `lineage_shrinkage` on mean MAE/MSE for this split. Output: `outputs/runs/v0.9-integrated-evoprior-additive/kang_2018_pbmc_ifnb/20260624T015655Z/`.
- `v0.10-kang-benchmark-alignment`: benchmark evidence collector aligns v0.6-v0.9 Kang records into JSON/CSV/Markdown evidence artifacts. Output: `outputs/runs/v0.10-public-benchmark-alignment/kang_2018_pbmc_ifnb_alignment/20260624T021659Z/`.
- `v0.10-synthetic-benchmark-alignment`: benchmark evidence collector aligns synthetic v0.7/v0.9 records into JSON/CSV/Markdown evidence artifacts. Output: `outputs/runs/v0.10-public-benchmark-alignment/synthetic_alignment/20260624T021655Z/`.
- `v0.11-public-benchmark-ingestion-plan`: registry validation, adapter planning, and ingestion-plan reporting run end-to-end without downloading external data or training models. Output: `outputs/runs/v0.11-external-public-benchmark-ingestion/20260624T023024Z/`.
- `v0.12-public-benchmark-baseline-run`: a public scPerturb-compatible Papalexi/Satija H5AD baseline run executes end-to-end with checksum-validated data, schema report, custom leave-one-perturbation split, leakage audit, locked internal metrics, and evidence artifacts. Output: `outputs/runs/v0.12-public-benchmark-baseline-run/scperturb_papalexi_2021_arrayed_rna_v012/20260624T150442Z/`.
- `v0.13-gears-norman-baseline`: a public Norman/scPerturb GEARS-compatible internal baseline run executes end-to-end with md5-validated data, schema report, internally generated seen0/seen1/seen2 split, leakage audit, locked internal metrics, DE20/DE50 recovery, and evidence artifacts. Output: `outputs/runs/v0.13-gears-norman-baseline/gears_norman_scperturb_v013/20260625T002742Z/`.
- `v0.14-gears-aligned-baseline`: the Norman package now includes an official-wrapper blocker report, an explicit random_combo split category, a weighted combo baseline, and a reviewer-facing package. Output: `outputs/runs/v0.14-gears-aligned-baseline/gears_norman_scperturb_v013/20260625T014719Z/`; blocker output: `outputs/runs/v0.14-official-gears-wrapper-blocked/gears_norman_scperturb_v013/20260625T014710Z/`.
- `v0.15-fast-neural-norman-baseline`: a fast sklearn MLP/PCA neural-style baseline trains and evaluates on the public Norman/scPerturb GEARS-compatible internal split with three seeds, seed summary metrics, model manifests, training curves, and evidence artifacts. Output: `outputs/runs/v0.15-fast-neural-norman-baseline/gears_norman_scperturb_v013/20260625T023033Z/`.
- `v0.16-official-gears-or-model-improvement-sprint`: a validation-selected residual correction baseline improves over the v0.14/v0.15 Norman internal baselines on test MAE, MSE, Pearson delta, and Spearman logFC. Output: `outputs/runs/v0.16-model-improvement-sprint/gears_norman_scperturb_v013/20260625T031612Z/`.
- `v0.17-norman-validated-residual-baseline`: the v0.16 residual model family is reproduced across seeds `0, 1, 2, 3, 4` with repeat-level CIs, ablations, negative controls, class breakdowns, and leakage stress checks. Output: `outputs/runs/v0.17-norman-validated-residual-baseline/gears_norman_scperturb_v013/20260625T100322Z/`.
- `v0.18-official-gears-reproduction-or-model-card-release`: an external review package is created for the v0.17 residual baseline, and a final official GEARS feasibility attempt is recorded as `import_ok_run_blocked`. Model metrics remain the v0.17 metrics. Release docs start at `docs/V18_EXTERNAL_REVIEW_INDEX.md`.
- `v0.19-public-repo-polish-and-official-gears-unblock`: public repo metadata, release smoke checks, official GEARS diagnostics, and artifact integrity checks are implemented for reviewer use. Smoke output: `outputs/runs/v0.19-release-smoke/20260625T223712Z/`; diagnostic output: `outputs/runs/v0.19-official-gears-diagnostics/20260625T223710Z/`; artifact manifest: `reports/v0.19_artifact_manifest.md`.
- `v0.20-github-release-or-official-gears-docker-env`: CI smoke workflow, release bundle generator, Docker/WSL GEARS environment route, v0.20 diagnostic output, and v0.20 artifact manifest are implemented for release review. Bundle: `outputs/release/v0.20/20260625T230630Z/`; diagnostic output: `outputs/runs/v0.20-official-gears-diagnostics/20260625T230451Z/`; artifact manifest: `reports/v0.20_artifact_manifest.md`.

## 消融提示

- `v0.5-synthetic-lineage-prior`: synthetic held-out cell-type results can be used as an implementation sanity check for lineage borrowing. They cannot be promoted to real-data biological evidence.
- `v0.6-real-multicell-lineage-benchmark`: held-out lineage suite has only n=2 clades and is underpowered; treat it as diagnostic context only.
- `v0.7-synthetic-gene-prior`: synthetic prior-modulated effects validate plumbing and ablation logic only.
- `v0.7-kang-gene-prior-compatibility`: because the source mode is `synthetic_gene_prior`, Kang v0.7 is compatibility-only and does not test real evolutionary-prior benefit.
- `v0.8-kang-real-gene-metadata-prior`: HGNC metadata coverage is 93.75% over evaluated Kang genes, but gene-prior correction does not improve over `lineage_shrinkage`; shuffled lineage correction matches the same metrics.
- `v0.9-kang-evoprior-additive`: the HGNC gene-prior additive variant does not beat the no-gene-prior additive variant on MAE; the component audit is mostly lineage-dominated, so do not attribute the integrated improvement to a true gene evolutionary prior.
- `v0.10-kang-benchmark-alignment`: evidence alignment confirms same-split comparability for Kang project splits, but it also confirms public external benchmark alignment is still blocked.
- `v0.11-public-benchmark-ingestion-plan`: metadata registration is not performance evidence; both example public benchmark records remain blocked for benchmarking.
- `v0.12-public-benchmark-baseline-run`: the selected split is custom benchmark-compatible rather than official leaderboard aligned, and the test suite is underpowered with n=2 held-out perturbations.
- `v0.13-gears-norman-baseline`: the Norman run is GEARS-compatible/internal rather than official GEARS aligned; `single_effect_additive_combo` is strongest among implemented transparent baselines under this exact split only.
- `v0.14-gears-aligned-baseline`: official GEARS remains blocked. `weighted_combo_additive` improves MAE/MSE narrowly under the v0.14 internal split, but `single_effect_additive_combo` remains slightly stronger on Pearson/Spearman.
- `v0.15-fast-neural-norman-baseline`: the trained neural-style baseline is reproducible, but it does not beat `weighted_combo_additive` on test MAE/MSE under the same v0.14 internal split.
- `v0.16-official-gears-or-model-improvement-sprint`: `weighted_pca_ridge_s075_a10` is validation-selected and improves test MAE/MSE/Pearson/Spearman under the same internal split, but it is still not official GEARS or leaderboard-comparable.
- `v0.17-norman-validated-residual-baseline`: five-seed stability is near deterministic because the selected PCA/ridge residual path has little stochasticity under the fixed split; this supports reproducibility, not broad external generalization.
- `v0.18-official-gears-reproduction-or-model-card-release`: official GEARS dependencies import inside `.venv_gears`, but the repository wrapper is feasibility-only and no official GEARS metrics are produced.
- `v0.19-public-repo-polish-and-official-gears-unblock`: release smoke and artifact checks support reproducibility review only. They do not create a new model result, official GEARS result, or leaderboard-comparable benchmark.
- `v0.20-github-release-or-official-gears-docker-env`: Docker/WSL GEARS files are an environment route only. They are not evidence that official GEARS was built, trained, evaluated, or matched to official metrics.

## 推测/未来工作

- 细胞谱系先验可能提升真实 held-out cell type 或 held-out context 外推，但还需要 v0.6 真实 multi-cell-type perturbation benchmark 验证。
- 基因演化/保守性先验可能提升 held-out perturbation 外推。
- 通路/调控网络先验可能提升 top DE gene recovery。
- v0.12 可以考虑 local public benchmark smoke run only if a small legally usable local fixture or already prepared local dataset exists.

这些都需要在固定 benchmark、统一 baselines 和多 seed 实验后才能升级为证据性声称。

## 明确不声称

- Do not claim v0.9 proves real evolutionary/conservation-prior benefit; HGNC metadata is not an orthology, conservation-score, or gene-age source.
- Do not claim the v0.9 Kang improvement is caused by the HGNC gene-prior component; the no-gene-prior additive variant is slightly better on MAE.
- Do not claim v0.9 implements a neural EvoPrior model.
- Do not claim v0.10 establishes public benchmark alignment; it only creates the evidence harness over existing project-defined runs.
- Do not claim v0.11 produces performance evidence; it only registers metadata and plans ingestion.
- Do not claim v0.12 is an official benchmark result, a leaderboard-comparable result, or evidence of general EvoPrior superiority.
- Do not claim v0.13 is an official GEARS result, a leaderboard-comparable result, SOTA, a neural GEARS reproduction, biological discovery, or evidence of general EvoPrior superiority.
- Do not claim v0.14 is an official GEARS result, a leaderboard-comparable result, SOTA, a neural GEARS reproduction, biological discovery, or evidence of general EvoPrior superiority.
- Do not claim v0.15 is an official GEARS result, a leaderboard-comparable result, SOTA, a PyTorch/GEARS reproduction, biological discovery, or evidence of general neural-model superiority.
- Do not claim v0.16 is an official GEARS result, a leaderboard-comparable result, SOTA, biological discovery, or evidence of general model superiority.
- Do not claim v0.17 is an official GEARS result, a leaderboard-comparable result, SOTA, biological discovery, or evidence of general model superiority.
- Do not claim v0.18 is an official GEARS result, a leaderboard-comparable result, SOTA, biological discovery, or evidence of general model superiority.
- Do not claim v0.19 is an official GEARS result, a leaderboard-comparable result, SOTA, biological discovery, or a new benchmark performance result.
- Do not claim v0.20 is an official GEARS result, a leaderboard-comparable result, SOTA, biological discovery, or a new benchmark performance result.

- 不声称任何真实公开数据集性能。
- 不声称 SOTA 或 near-SOTA。
- 不声称 lineage prior 已经在真实生物数据上有效；v0.5 只实现了第一个非神经谱系先验 baseline 和 synthetic sanity check。
- 不声称真实 evolutionary-prior benefit、pathway prior 或 neural EvoPrior 已经实现。
- 不声称 v0.3 的 Papalexi split 是公开 leaderboard 或论文 benchmark。
- 不声称真实数据指标说明生物学发现；它们只说明当前 pipeline 可以运行。
- 不声称 v0.4 repeated metrics establish model superiority; leave-one perturbation is underpowered.
- 不声称 retrieval/PDS is meaningful for held-out perturbations absent from train candidate profiles.
- 不声称 Papalexi v0.5 compatibility metrics 说明谱系先验有效；该数据在当前配置下只有一个 cell type/cell line。
- 不声称 v0.6 Kang result generalizes beyond PBMC IFN-beta stimulation.
- 不声称 v0.6 is public-leaderboard comparable.
- 不把 tau audit 中测试集表现最好的 tau 当作调参选择结果。
- 不声称 v0.7 Kang metrics 说明 real evolutionary-prior benefit；当前 prior 是 synthetic/placeholder。
- 不声称 v0.8 HGNC metadata-prior metrics 说明 real evolutionary/conservation-prior benefit；当前没有 orthology、conservation score 或 gene-age source。
