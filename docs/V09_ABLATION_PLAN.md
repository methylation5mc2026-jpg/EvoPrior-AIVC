# v0.9 Ablation Plan

Status: planned comparisons for synthetic and Kang integrated additive runs.

## Required Comparisons

Synthetic integrated benchmark:

1. `control_mean`
2. `mean_delta`
3. `lineage_shrinkage`
4. `evoprior_additive_no_gene_prior`
5. `evoprior_additive_hgnc_gene_prior`
6. `evoprior_additive_shuffled_gene_prior`
7. `evoprior_additive_gene_prior_disabled`

Kang integrated benchmark:

1. `control_mean`
2. `mean_delta`
3. `hierarchical_additive`
4. `ridge_cv`
5. `lineage_shrinkage`
6. `gene_prior_correction_lineage_shrinkage`
7. `evoprior_additive_no_gene_prior`
8. `evoprior_additive_hgnc_gene_prior`
9. `evoprior_additive_shuffled_gene_prior`
10. `evoprior_additive_gene_prior_disabled`

## Metrics

- MAE
- MSE
- Pearson delta correlation
- Spearman logFC correlation
- DE recovery top-k
- per-heldout-cell-type metrics
- prior-covered and prior-missing subset metrics
- component magnitude summary
- component correlation summary

## Negative Controls

- shuffled HGNC metadata prior;
- gene-prior component disabled;
- lineage component disabled where relevant.

## Interpretation Rules

Allowed:

- compare metrics within the project-defined split;
- report whether integrated additive did or did not improve over `lineage_shrinkage`;
- inspect component magnitudes and whether the gene-prior component collapses.

Forbidden:

- SOTA;
- public benchmark comparability;
- general EvoPrior success;
- true evolutionary-prior benefit;
- biological discovery.
