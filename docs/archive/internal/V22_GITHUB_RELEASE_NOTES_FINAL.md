# EvoPrior-AIVC v0.22 Public Review Candidate

## Highlights

- Validated Norman/scPerturb residual baseline on a fixed internal GEARS-compatible split.
- Five-seed result for `weighted_pca_ridge_s075_a10`.
- Critical leakage stress checks passed.
- Model card, benchmark card, reproducibility runbook, and public demo guide included.
- No-data CI smoke path and release bundle path included for reviewers.
- Release bundle: `outputs/release/v0.22/20260626T000119Z/`.
- Artifact manifest: `reports/v0.22_artifact_manifest.md`.
- Release smoke: `outputs/runs/v0.19-release-smoke/20260626T000135Z/`, status `pass`.

## Main Result

Dataset: `NormanWeissman2019_filtered.h5ad`, scPerturb Zenodo record 13350497, version 1.4.

Checksum: `c870e6967d91c017d9da827bab183cd6`.

Split: fixed internal GEARS-compatible seen0/seen1/seen2/random_combo split, not official GEARS.

| model | seeds | MAE | MSE | Pearson delta | Spearman logFC |
| --- | ---: | ---: | ---: | ---: | ---: |
| v0.14 weighted combo additive | 1 | 0.5660 | 6.6759 | 0.7599 | 0.6390 |
| v0.15 fast MLP/PCA | 3 | 0.5877 | 7.5517 | 0.7134 | 0.6317 |
| v0.17 validated residual baseline | 5 | 0.430778 | 3.668870 | 0.869224 | 0.784976 |

Primary output:

```text
outputs/runs/v0.17-norman-validated-residual-baseline/gears_norman_scperturb_v013/20260625T100322Z/
```

## How To Reproduce

No-data review:

```powershell
python -m pip install -e ".[dev]"
python -m pytest -p no:cacheprovider --basetemp .tmp_pytest_local tests/test_release_smoke_config.py tests/test_release_artifact_manifest.py tests/test_official_gears_diagnostics.py tests/test_ci_workflow_static.py
python scripts/check_ci_workflow.py --workflow .github/workflows/ci.yml
python scripts/run_release_smoke.py --config configs/experiment/release_smoke_v019.yaml
```

With local data:

```powershell
python scripts/prepare_gears_norman.py --config configs/data/gears_norman_v013.yaml --dry-run
python scripts/run_norman_residual_multiseed.py --config configs/experiment/gears_norman_v017_multiseed_residual.yaml
python scripts/check_release_artifacts.py
```

## Data Requirement

Place `NormanWeissman2019_filtered.h5ad` at:

```text
data/raw/NormanWeissman2019_filtered.h5ad
```

Expected md5:

```text
c870e6967d91c017d9da827bab183cd6
```

Raw data is not included in the repository or release bundle.

## What Is Not Claimed

- Not official GEARS.
- Not leaderboard-comparable.
- Not SOTA.
- Not a biological discovery.
- Not a clinical or diagnostic tool.
- Not broad model superiority across perturbation benchmarks.

## Known Limitations

- The split is internal GEARS-compatible, not an imported official GEARS split.
- Metrics are internal compatible metrics, not official leaderboard metrics.
- The selected PCA/ridge residual path is nearly deterministic, so five-seed stability supports reproducibility rather than broad uncertainty.
- Docker and official GEARS training remain blocked unless a reviewer supplies a working Docker or official GEARS environment and implements exact official split/metric alignment.

## Next Steps

- Publish the repository and attach this release note to the GitHub release.
- Run GitHub-hosted CI after remote publication.
- Optionally execute the Docker route if Docker is available.
- Start `v0.23-github-publish-or-project-page-assets` only after this release candidate is committed and tagged.
