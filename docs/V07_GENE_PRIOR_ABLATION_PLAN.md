# v0.7 Gene Prior Ablation Plan

Status: ablation protocol for synthetic and Kang compatibility runs.

## Required Comparisons

Synthetic benchmark:

- v0.6-style baselines,
- `lineage_shrinkage`,
- `gene_prior_correction` over `control_mean`,
- `gene_prior_correction` over `mean_delta`,
- `gene_prior_correction` over `lineage_shrinkage`,
- shuffled gene-prior correction negative control,
- missing-prior fallback control.

Real Kang run:

- `lineage_shrinkage` base baseline,
- gene-prior correction over `control_mean`,
- gene-prior correction over `lineage_shrinkage`,
- gene-prior correction over `mean_delta`,
- shuffled prior correction,
- missing/fallback behavior.

If the Kang prior source is synthetic/placeholder, the run is compatibility-only and must not be interpreted as biological/evolutionary evidence.

## Leakage Audit

Every v0.7 run must report:

- gene-prior source and source version,
- checksum for generated/loaded prior table,
- feature columns,
- feature missingness,
- coverage over evaluated genes,
- whether any test response data was used to construct prior features,
- shuffled-prior negative-control behavior,
- correction magnitude summary,
- top corrected genes for inspection,
- missing-prior fallback behavior.

## Metrics

Primary metrics:

- MAE,
- MSE,
- Pearson delta correlation,
- Spearman logFC correlation,
- DE recovery top-k.

Subset metrics:

- prior-covered genes,
- prior-missing genes,
- prior-modulated synthetic genes.

## Interpretation Rules

Allowed:

- synthetic benchmark confirms expected gene-prior plumbing;
- compatibility-only Kang run confirms feature mapping and correction runner work;
- real improvement can only be claimed if a meaningful, versioned gene-prior table is used.

Forbidden:

- using shuffled-prior wins as evidence of biological signal,
- selecting hyperparameters from test metrics,
- claiming causal evolutionary mechanisms,
- claiming SOTA or leaderboard comparability.
