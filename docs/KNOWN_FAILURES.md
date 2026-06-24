# 已知失败与风险

## 当前已知风险

1. 第一公开真实数据集已锁定为 Papalexi/scPerturb，但它只适合真实数据 plumbing 和 baseline hardening，不适合谱系验证。
2. 文献地图是初始种子，未完成系统综述。
3. 当前指标实现只覆盖最小玩具案例；真实单细胞评测需要补充 per-group breakdown、DE 方法和置信区间。
4. 当前切分实现只做基础 held-out 标签检查；复杂 context split 需要更严格的组合键审计。
5. 目前只下载、校验并处理了一个小型 Papalexi H5AD；尚未接入真实 multi-cell-type perturbation 数据。
6. v0.2 只验证 synthetic data pipeline 和 baseline plumbing；v0.3/v0.4 才验证真实数据 plumbing 和强化基线。
7. v0.2 的 `heldout_perturbation` 只测试 synthetic `pert_c` fallback，不代表真实 unseen perturbation 泛化能力。
8. 尚未实现 EvoPrior 神经模块、基因保守性先验或通路网络先验；v0.5 只实现了第一个非神经细胞谱系先验 baseline。
9. 当前 preprocessing 尚未与任何公开论文 baseline 完全对齐。
10. v0.3 选择的 Papalexi/scPerturb 数据只有一个 cell type/cell line，不能测试谱系泛化。
11. v0.3 数据没有 donor 字段，不能测试 donor split。
12. v0.3 使用 project-defined split，没有与 Papalexi、scPerturb、pertpy 或 GEARS 的公开 split 对齐。
13. v0.3 held-out `pdl1` 只有两个 guide-level pseudobulk groups，其中一个 group 只有 24 cells，指标波动会很大。
14. v0.3 使用 top-variance 3,000 genes 的本地 smoke 配置，不代表完整基因空间评测。
15. v0.4 leave-one-perturbation suite is underpowered: only perturbations with at least two guide-level groups are eligible.
16. v0.4 retrieval metrics are not meaningful for held-out perturbations absent from train candidate profiles; these rows are marked underpowered/not meaningful.
17. v0.4 confidence intervals use a simple normal approximation and are descriptive only.
18. v0.4 sensitivity audit shows MAE can move substantially across top-gene and min-cell settings; this setup should not be optimized against test metrics.
19. Public benchmark alignment remains incomplete; current Papalexi split is not a GEARS/CZI/Systema/CPA/scGen benchmark.
20. v0.5 synthetic lineage benchmark 是理想化生成过程，不能说明真实生物谱系泛化。
21. v0.5 Papalexi compatibility run 是 no-op/fallback 检查；Papalexi 当前配置只有一个 cell type/cell line，不能识别 lineage signal。
22. v0.5 `LineageShrinkageBaseline` 是 non-neural shrinkage baseline，不是 EvoPrior neural model。
23. v0.5 尚未选择真实 multi-cell-type perturbation benchmark；`docs/V05_REAL_MULTICELL_DATASET_SCOUTING.md` 只是侦察记录。
24. 如果未来候选数据只有多个 cancer cell lines，而不是明确发育谱系，只能声称 context/cell-line transfer，不能声称 biological lineage validation。
25. v0.6 Kang benchmark 只有一个非对照 perturbation (`stim`)，不能测试多扰动泛化，也不适合 retrieval/PDS。
26. v0.6 `megakaryocytes` 在 donor-level pseudobulk 后 test groups 太少，被 held-out cell-type suite 跳过。
27. v0.6 held-out lineage suite 只有 `lymphoid` 和 `myeloid` 两个 clades，CI 标记 underpowered，不应用于强结论。
28. v0.6 lineage mapping 是 coarse operational PBMC prior，不是 ontology-grade lineage truth。
29. v0.6 为保留 donor-matched ctrl/stim pairs 使用 `min_cells_per_group=5`，稀有群体 pseudobulk 噪声可能更高。
30. v0.6 benchmark 仍是 project-defined split，不是公开 leaderboard 或论文官方 split。
31. v0.7 synthetic gene-prior benchmark uses a known synthetic prior-modulated generator; it validates plumbing and ablation logic only.
32. v0.7 strong bases such as `mean_delta` and `lineage_shrinkage` may already capture synthetic global gene modulation, so correction over those bases is not required to improve for the sanity check.
33. v0.7 Kang gene-prior source mode is `synthetic_gene_prior`; the run is compatibility-only and does not test real evolutionary-prior benefit.
34. v0.7 `GenePriorCorrectionBaseline` is non-neural residual correction, not an EvoPrior neural model.
35. v0.8 HGNC metadata is a real functional/gene-metadata source, not an orthology/conservation/gene-age source.
36. v0.8 HGNC keyword-derived `is_immune_related` is coarse metadata, not biological discovery.
37. v0.8 Kang ablation does not show improvement over `lineage_shrinkage`; shuffled lineage correction matches lineage metrics.
38. v0.8 still uses the same single-stimulus Kang PBMC IFN-beta project-defined split, so no public benchmark or multi-perturbation generalization claim is allowed.
39. v0.9 `EvoPriorAdditiveModel` is a transparent non-neural additive model, not a neural EvoPrior implementation.
40. v0.9 Kang integrated additive improvement over `lineage_shrinkage` should not be attributed to HGNC gene metadata alone; the no-gene-prior additive variant has slightly lower MAE than the HGNC variant.
41. v0.9 component audits are mostly lineage-dominated, and shuffled gene-prior component magnitude is non-zero, so no true evolutionary/conservation-prior benefit claim is allowed.
42. v0.10 benchmark alignment does not import external public benchmark data or official external split definitions; public benchmark alignment remains blocked.
43. v0.10 evidence tables can show same-project split comparability, but they do not make outputs from different datasets or different split policies directly comparable.
44. v0.10 treats n=0 blank metric means as missing values; they should not be interpreted as finite performance values.
45. v0.11 metadata registration is not benchmark evidence; successful planning does not imply a model was run.
46. v0.11 example public benchmark records remain blocked because no large external data or official public split was imported.
47. v0.11 local-fixture validation count is zero in the current run; future smoke runs need a small legally usable local fixture or already prepared local dataset.
48. v0.12 Papalexi/scPerturb run is public-data and benchmark-compatible, but its split is custom and not official leaderboard aligned.
49. v0.12 leave-one-perturbation suite is underpowered: only `etv7` and `pdl1` have at least two guide-level pseudobulk test groups under the configured threshold.
50. v0.12 metrics are internal compatible metrics, not official GEARS/scPerturb leaderboard metrics.
51. v0.12 `evoprior_additive_no_prior` disables lineage and gene priors because Papalexi has one configured cell type and no relevant real prior claim; it must not be presented as a full EvoPrior prior-benefit result.

## 失败记录模板

```text
Failure ID:
Date:
Experiment ID:
Symptom:
Root cause:
Evidence:
Impact:
Mitigation:
Preserved artifacts:
Rollback note:
```
