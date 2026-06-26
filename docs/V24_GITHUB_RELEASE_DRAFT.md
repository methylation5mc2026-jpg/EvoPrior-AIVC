# v0.24 GitHub Release Draft

## Title

EvoPrior-AIVC v0.24: Public Review Package and Website Integration Assets

## Tag

`v0.24-github-push-and-release-or-website-integration`

## Summary

This release packages EvoPrior-AIVC for public GitHub review and personal website or mentor presentation. It keeps the validated v0.17 Norman residual baseline as the benchmark evidence source and adds publish commands, Release text, link-audit guidance, website copy, and a compact final presentation summary.

## Main Evidence

- Dataset: `NormanWeissman2019_filtered.h5ad`
- Dataset md5: `c870e6967d91c017d9da827bab183cd6`
- Split: fixed internal GEARS-compatible Norman seen0/seen1/seen2/random_combo split
- Output: `outputs/runs/v0.17-norman-validated-residual-baseline/gears_norman_scperturb_v013/20260625T100322Z/`
- Primary model: `weighted_pca_ridge_s075_a10`
- Seeds: `0, 1, 2, 3, 4`

| Metric | Value |
| --- | ---: |
| MAE | 0.430778 |
| MSE | 3.668870 |
| Pearson delta | 0.869224 |
| Spearman logFC | 0.784976 |

## Included

- Public README and review map.
- Model card, benchmark card, and reproducibility runbook.
- GitHub publish guide and Release body.
- Website integration assets.
- Public link audit and post-publish checklist.
- Release bundle config and artifact manifest refresh.

## Not Included

- Raw H5AD data.
- Generated benchmark outputs.
- Model checkpoints.
- Virtual environments or caches.

## Allowed Claim

We provide a reproducible public-review package around a validated internal GEARS-compatible Norman residual baseline, with documented data provenance, split, metrics, and claim boundaries.

## Forbidden Claims

- Official GEARS result.
- Leaderboard-comparable result.
- SOTA or near-SOTA.
- Biological discovery.
- Clinical use.
- General model superiority.
- GitHub or website publication already completed by v0.24.

## Suggested Release Assets

Attach no raw data. If an archive is needed, use the generated review bundle under `outputs/release/v0.24/<timestamp>/` after verifying that it contains only safe reference files.
