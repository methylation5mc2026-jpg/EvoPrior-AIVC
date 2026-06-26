# v0.20 GitHub Release Plan

## Scope

v0.20 prepares the repository for a GitHub-facing review release. It does not change the v0.17 model, benchmark split, seed list, metrics, or claim boundary.

## Release Identity

- Expected tag: `v0.20-github-release-or-official-gears-docker-env`
- Rollback tag: `v0.19-public-repo-polish-and-official-gears-unblock`
- Primary validated result: v0.17 Norman residual baseline
- Dataset md5: `c870e6967d91c017d9da827bab183cd6`

## Evidence Pointers

- Config: `configs/experiment/gears_norman_v017_multiseed_residual.yaml`
- Command: `python scripts/run_norman_residual_multiseed.py --config configs/experiment/gears_norman_v017_multiseed_residual.yaml`
- Output: `outputs/runs/v0.17-norman-validated-residual-baseline/gears_norman_scperturb_v013/20260625T100322Z/`
- Split manifest: `outputs/runs/v0.17-norman-validated-residual-baseline/gears_norman_scperturb_v013/20260625T100322Z/split_manifest.csv`
- Smoke result: `outputs/runs/v0.19-release-smoke/20260625T230440Z/`
- v0.19 artifact manifest: `reports/v0.19_artifact_manifest.md`

## Bundle Command

```powershell
python scripts/make_release_bundle.py --config configs/release/v020_release_bundle.yaml
```

Output pattern:

```text
outputs/release/v0.20/<timestamp>/
```

Latest local output:

```text
outputs/release/v0.20/20260625T230630Z/
```

The bundle contains small reviewer-facing files only. It excludes raw data, large outputs, checkpoints, virtual environments, caches, and `.git`.

## Claim Boundary

Allowed: repository release readiness and a reproducible review package around the validated v0.17 internal GEARS-compatible Norman result.

Forbidden: official GEARS result, leaderboard comparability, SOTA, biological discovery, or general model superiority.
