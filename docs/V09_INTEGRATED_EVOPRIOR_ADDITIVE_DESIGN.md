# v0.9 Integrated EvoPrior Additive Design

Status: design and claim-boundary document for `v0.9-integrated-evoprior-additive-model`.

## Scientific Hypothesis

A transparent additive model may improve perturbation-response prediction by combining:

- baseline control-state and global response information,
- perturbation-level response,
- lineage-weighted borrowing across related cell types,
- real HGNC gene-metadata priors,
- residual shrinkage and regularization.

The goal is interpretability and controlled integration, not SOTA performance.

## Model Family

`EvoPriorAdditiveModel` is non-neural. It uses only pandas, numpy, and sklearn-style linear components.

The model predicts deltas:

```text
predicted_delta[c, p, g] =
    global_delta[g]
  + perturbation_component[p, g]
  + lineage_component[c, p, g]
  + gene_prior_component[g]
```

Where:

- `g` is gene,
- `p` is perturbation,
- `c` is cell type,
- all components are fit only on training groups,
- held-out cell-type perturbed deltas are never used in training,
- held-out cell-type controls may be used only under the existing `control_observed_ood` policy.

## Components

- `global_delta`: mean training delta per gene.
- `perturbation_component`: perturbation-specific training mean residual after global delta.
- `lineage_component`: weighted residual from related training cell types for the same perturbation; weights decay with lineage distance and `tau_lineage`.
- `gene_prior_component`: optional residual correction learned from gene-prior features with ridge shrinkage.
- `final_delta`: sum of components.

## Parameters

- `tau_lineage`: lineage distance decay.
- `alpha_shrinkage`: ridge regularization for gene-prior residual fitting.
- `use_gene_prior`: enable/disable gene-prior component.
- `use_lineage_prior`: enable/disable lineage component.
- `gene_prior_mode`: `residual_additive` or `disabled`.
- `fallback_mode`: `global` or `perturbation`.
- `min_groups_per_effect`: minimum groups before using an empirical perturbation/cell-type effect.

## Leakage Rules

Forbidden:

- fitting any component on held-out target perturbed deltas,
- selecting hyperparameters from test metrics,
- deriving HGNC/gene-prior features from perturbation response,
- treating shuffled-prior behavior as biological evidence.

Allowed:

- using training deltas,
- using held-out controls under `control_observed_ood`,
- using documented lineage mapping,
- using HGNC metadata features from v0.8.

## Allowed Claims

- integrated additive model implemented and tested;
- component breakdown is available for inspection;
- synthetic benchmark validates integration plumbing and ablation logic;
- Kang ablation compares the integrated model to v0.6/v0.8 baselines;
- results are preliminary and Kang split-specific.

## Forbidden Claims

- SOTA or public leaderboard alignment;
- general EvoPrior effectiveness;
- biological discovery;
- true evolutionary/conservation-prior benefit from HGNC-only features;
- neural EvoPrior success.

## Rollback

Rollback point: `v0.8-real-versioned-gene-prior-source`.
