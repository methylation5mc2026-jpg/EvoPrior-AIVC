# v0.6 Real Multi-Cell-Type Dataset Selection

Status: selected and benchmarked one small real public dataset for v0.6 implementation.
Checked on 2026-06-23.

## Decision Summary

Selected dataset: `kang_2018_pbmc_ifnb`

This dataset is selected because it is a real public PBMC perturbation dataset with multiple immune cell types, a clear IFN-beta stimulation/control condition, patient/replicate metadata, a manageable H5AD file, and a stable Figshare file with md5 metadata.

The selected dataset is suitable for a first real multi-cell-type lineage-aware benchmark, but only with a narrow claim boundary:

- It tests one cytokine stimulation response (`stim` vs `ctrl`) across PBMC immune cell types.
- It does not test many perturbation identities.
- It does not establish general lineage-prior superiority.
- It is not a public leaderboard split.

Main benchmark output:

```text
outputs/runs/v0.6-real-multicell-lineage-benchmark/kang_2018_pbmc_ifnb/20260623T092131Z/
```

Tau sensitivity output:

```text
outputs/runs/v0.6-real-multicell-lineage-tau-audit/kang_2018_pbmc_ifnb/20260623T092131Z/
```

## Selected Dataset Decision Record

- Dataset ID: `kang_2018_pbmc_ifnb`
- Reason: small, public, real PBMC dataset with multiple immune cell types and matched control/stimulated conditions across donors.
- Risk: one non-control perturbation means perturbation-overlap is trivial; lineage benefit may be underpowered or dominated by broad IFN response.
- Expected split: held-out cell-type suite with control-observed OOD mode. Held-out cell-type stimulated pseudobulks are test only; held-out cell-type controls are allowed as input control state but not used as train target deltas.
- Expected failure mode: some rare cell types may have too few donor-level control/stim pairs after `min_cells_per_group`; those cell types must be skipped and reported.
- Fallback plan: if Kang fails schema, coverage, or leakage gates, do not tag v0.6 success. Keep scouting/config/adapters only and ask for a manual dataset choice.

## Suitability Gate

Hard requirements:

| Requirement | Kang 2018 PBMC IFN-beta status |
| --- | --- |
| Real public perturbation dataset | Pass. Public Kang et al. 2018 PBMC stimulation dataset. |
| At least 3 cell types/states | Pass. Public tutorials show 8 PBMC cell types. |
| Clear perturbation labels | Pass. `label` contains `ctrl` and `stim`. |
| Clear control condition | Pass. `ctrl` is the control condition. |
| Same/overlapping perturbations across cell types | Pass with limitation. `stim` exists across multiple PBMC cell types, but there is only one non-control perturbation. |
| AnnData/H5AD or clean conversion | Pass. Figshare file is `kang.h5ad`. |
| Local run feasible | Pass. Figshare API reports 38,356,412 bytes. |
| Leakage-safe held-out cell-type split | Pass if enough donor-level pseudobulk groups remain after filtering. |

Strong preferences:

| Preference | Kang 2018 PBMC IFN-beta status |
| --- | --- |
| Donor/batch metadata | Pass. Tutorials describe patient/replicate metadata. |
| Lineage-rich biological family | Pass. PBMC immune subsets support a coarse immune lineage tree. |
| Enough groups per cell_type x perturbation | Tentative pass; must be validated after pseudobulk. |
| Size below 2 GB | Pass. About 38 MB. |
| Existing common use | Pass. Used in pertpy and single-cell best-practices tutorials. |

## Candidate Decision Table

| dataset_id | source | modality | perturbation type | cell types | perturbations | approximate cells | approximate size | format | controls? | donor/batch? | overlap across cell types? | candidate split | risks | decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `kang_2018_pbmc_ifnb` | Figshare / pertpy / Kang et al. | scRNA-seq | IFN-beta stimulation | 8 PBMC cell types reported in tutorials | 2 labels: ctrl/stim | 24,673 cells reported in tutorials | 38,356,412 bytes from Figshare API | H5AD | yes | replicate/patient | yes, single non-control condition | held-out cell type, control-observed OOD | only one perturbation; possible sparse rare cell types | selected |
| `virtual_cell_challenge_pbmc_cytokine` | Virtual Cell Challenge | scRNA-seq | cytokine perturbations | 18 cell types reported by source | 90 cytokine responses reported by source | large PBMC corpus | not confirmed locally | likely hosted challenge data | yes, likely | 12 donors reported | likely yes | held-out cell type/donor | access and size need confirmation; may exceed local lightweight scope | future |
| `hagai_2018` | pertpy/scPerturb | scRNA-seq | dsRNA/IFNB stimulation | fibroblast/phagocyte across species | few stimuli | not checked | not checked | H5AD via pertpy | likely | species/replicate | partial | held-out cell type/species-context | cross-species context complicates lineage interpretation | backup |
| `mcfarland_2020` | pertpy/scPerturb | scRNA-seq | drugs and CRISPRi | many cancer cell lines | many | large | not checked | H5AD via pertpy | likely | cell-line/batch | likely | held-out cell line | cell-line hierarchy is not developmental lineage; likely larger | future |
| `frangieh_2021_rna` | pertpy/Broad | CITE-seq RNA | CRISPR perturbations | melanoma/TIL co-culture states | ~750 perturbations | >218k cells | not checked | H5AD via pertpy/Broad | likely | patient/model | likely | held-out cell state | larger, complex co-culture, adapter burden | future |
| `papalexi_2021` | existing v0.3/v0.4 data | ECCITE-seq RNA | antibody/gene perturbation labels | 1 configured cell type | many labels | 52 MB raw file | 52,339,395 bytes | H5AD | yes | no donor | no | none | cannot test lineage | rejected |
| `norman_2019` | pertpy/GEARS ecosystem | Perturb-seq | CRISPR overexpression | mainly one cell line/context | many | medium | not checked | H5AD | yes | weak | no real cell-type lineage | held-out perturbation only | not a lineage benchmark | rejected for v0.6 |

## Sources

- Kang Figshare article: <https://figshare.com/articles/dataset/Kang_HM_Subramaniam_M_Targ_S_Nguyen_M_et_al_2017/19397624>
- Kang Figshare file metadata API: <https://api.figshare.com/v2/articles/19397624/files>
- pertpy Kang loader documentation: <https://pertpy.readthedocs.io/en/latest/api/data/pertpy.data.kang_2018.html>
- Single-cell best-practices Kang pseudobulk tutorial: <https://www.sc-best-practices.org/conditions/differential_gene_expression.html>
- pertpy dataset index: <https://pertpy.readthedocs.io/en/stable/api/datasets_index.html>
- Virtual Cell Challenge datasets: <https://virtualcellchallenge.org/datasets>

## Claim Boundary

If the benchmark runs end-to-end, v0.6 may claim only:

- a real multi-cell-type PBMC IFN-beta benchmark was added;
- a coarse immune lineage mapping was documented;
- `LineageShrinkageBaseline` was compared against v0.4 baselines on documented held-out cell-type splits;
- any win/loss is preliminary, dataset-specific, and limited to this single-stimulation setting.

v0.6 must not claim:

- general lineage-prior superiority;
- SOTA or near-SOTA;
- neural EvoPrior performance;
- evolutionary-prior benefit;
- public benchmark leaderboard comparability.

## v0.6 Gate Outcome

- Prepare dry-run: passed.
- Download: passed; md5 `adb2246232e8493031c576982c0c02a3` verified.
- Schema report: passed; 24,673 cells, 15,706 genes, 8 cell types, 2 perturbation labels.
- Pseudobulk: passed with `min_cells_per_group=5`.
- Held-out cell-type eligibility: 7 eligible cell types; `megakaryocytes` skipped.
- Held-out lineage suite: ran for `lymphoid` and `myeloid`, but n=2 and underpowered.
- Retrieval/PDS: skipped because there is only one non-control perturbation.
