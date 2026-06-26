# v0.24 Post-Publish Checklist

## GitHub Repository

- [ ] `origin` points to the intended public repository.
- [ ] Branch `feat/github-push-release-website-v024` is pushed.
- [ ] Tag `v0.24-github-push-and-release-or-website-integration` is pushed.
- [ ] README renders correctly.
- [ ] License status is acceptable for the intended audience.
- [ ] No raw H5AD, generated outputs, caches, virtual environments, or credentials are present.

## GitHub Release

- [ ] Release title matches `docs/V24_GITHUB_RELEASE_DRAFT.md`.
- [ ] Release body keeps the claim boundary.
- [ ] No raw data or large generated outputs are uploaded.
- [ ] Release links point to model card, benchmark card, reproducibility runbook, and public data guide.

## CI And Smoke

- [ ] GitHub-hosted Actions run completes.
- [ ] No-data smoke path is documented for fresh clones.
- [ ] Local heavy data reproduction remains opt-in and documented.

## Website Or Portfolio

- [ ] Project card uses the short summary from `docs/V24_WEBSITE_INTEGRATION_ASSETS.md`.
- [ ] Result table labels the split as internal GEARS-compatible.
- [ ] Website links point to public GitHub pages, not local Windows paths.
- [ ] No SOTA, official GEARS, leaderboard, or biological discovery language appears.

## Mentor Review

- [ ] Send README, model card, benchmark card, release draft, and final presentation summary.
- [ ] State remaining blockers: official GEARS metrics, official split import, Docker-hosted validation, and public website deployment.
