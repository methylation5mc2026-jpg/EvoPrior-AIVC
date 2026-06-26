# v0.25 Post-Publish Verification

## Repository

- [ ] `https://github.com/methylation5mc2026-jpg/EvoPrior-AIVC` opens publicly or with the intended visibility.
- [ ] README renders correctly.
- [ ] Branch `feat/github-publish-execution-v025` exists on GitHub.
- [ ] Tags `v0.24-github-push-and-release-or-website-integration` and `v0.25-github-publish-execution-and-final-link-package` exist on GitHub.
- [ ] No raw H5AD files are visible in the repository.
- [ ] No generated `outputs/runs/`, release bundles, virtual environments, caches, or secrets are visible.

## Release

- [ ] GitHub Release exists for `v0.24-github-push-and-release-or-website-integration`.
- [ ] Release notes render from `docs/V24_GITHUB_RELEASE_DRAFT.md`.
- [ ] Release text keeps the claim boundary.
- [ ] No raw data or generated benchmark outputs are attached.

## CI And Smoke

- [ ] GitHub Actions starts after push.
- [ ] CI passes, or a known local-only blocker is documented.
- [ ] Local smoke remains reproducible with `python scripts/run_release_smoke.py --config configs/experiment/release_smoke_v019.yaml`.

## Public Links

- [ ] README link works.
- [ ] Model card link works.
- [ ] Benchmark card link works.
- [ ] Reproducibility runbook link works.
- [ ] Public data guide link works.
- [ ] Project website link works after website integration.

## GitHub Metadata

- [ ] About description is set.
- [ ] Topics are set.
- [ ] Website field is set after the project page exists.
- [ ] License status is acceptable for public sharing.

## Scientific Boundary

- [ ] Public text says internal GEARS-compatible, not official GEARS.
- [ ] Public text does not say SOTA or leaderboard-comparable.
- [ ] Public text does not claim biological discovery or clinical use.
