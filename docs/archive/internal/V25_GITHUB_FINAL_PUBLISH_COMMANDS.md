# v0.25 GitHub Final Publish Commands

Run these in PowerShell from the local repository.

## Mode A: Add Existing GitHub Remote And Push

```powershell
cd C:\Users\HiC3C\Documents\AIVC
git status --short
git remote add origin https://github.com/methylation5mc2026-jpg/EvoPrior-AIVC.git
git remote -v
git push -u origin feat/github-publish-execution-v025
git push origin v0.24-github-push-and-release-or-website-integration
git push origin v0.25-github-publish-execution-and-final-link-package
```

## Mode B: If The Remote Already Exists

```powershell
git remote set-url origin https://github.com/methylation5mc2026-jpg/EvoPrior-AIVC.git
git remote -v
git push -u origin feat/github-publish-execution-v025
git push origin --tags
```

## Mode C: Publish Main Branch

Use this only if you want the repository default branch to contain the full v0.25 package immediately.

```powershell
git switch main
git merge --no-ff feat/github-publish-execution-v025
git push -u origin main
git push origin --tags
```

## GitHub CLI Release Creation

Only after installing and authenticating `gh`:

```powershell
gh auth status
gh release create v0.24-github-push-and-release-or-website-integration --title "EvoPrior-AIVC v0.24 Public Review Release" --notes-file docs/V24_GITHUB_RELEASE_DRAFT.md
```

## Manual GitHub Release Creation

1. Open `https://github.com/methylation5mc2026-jpg/EvoPrior-AIVC`.
2. Open Releases.
3. Draft a new release.
4. Select tag `v0.24-github-push-and-release-or-website-integration`.
5. Paste `docs/V24_GITHUB_RELEASE_DRAFT.md`.
6. Do not upload raw H5AD files, generated benchmark outputs, virtual environments, caches, or local-only outputs.

## Repository Settings

- About description: `Reproducible single-cell perturbation prediction benchmark package with a validated internal GEARS-compatible Norman residual baseline.`
- Topics: `single-cell`, `perturb-seq`, `benchmark`, `bioinformatics`, `reproducibility`, `gears-compatible`, `norman`, `machine-learning`
- Website: add the personal project page URL after it exists.

## Post-Push Checks

```powershell
git ls-remote origin HEAD
git ls-remote origin refs/heads/feat/github-publish-execution-v025
git ls-remote origin refs/tags/v0.24-github-push-and-release-or-website-integration
git ls-remote origin refs/tags/v0.25-github-publish-execution-and-final-link-package
```
