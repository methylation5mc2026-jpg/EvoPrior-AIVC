# v0.26 GitHub Release Execution Log

## Release Status

The GitHub Releases page currently shows no releases.

Observed page:

`https://github.com/methylation5mc2026-jpg/EvoPrior-AIVC/releases`

## Preferred Release

- Tag: `v0.25-github-publish-execution-and-final-link-package`
- Title: `EvoPrior-AIVC v0.25 Public Review Release`
- Notes source: `docs/V24_GITHUB_RELEASE_DRAFT.md`

## Manual Release Steps

1. Open `https://github.com/methylation5mc2026-jpg/EvoPrior-AIVC/releases`.
2. Click `Draft a new release`.
3. Choose tag `v0.25-github-publish-execution-and-final-link-package`.
4. Title: `EvoPrior-AIVC v0.25 Public Review Release`.
5. Paste the body from `docs/V24_GITHUB_RELEASE_DRAFT.md`.
6. Do not attach raw H5AD files, generated benchmark outputs, virtual environments, caches, or local-only artifacts.

## Optional CLI Path

Use only if GitHub CLI is installed and authenticated:

```powershell
gh auth status
gh release create v0.25-github-publish-execution-and-final-link-package --title "EvoPrior-AIVC v0.25 Public Review Release" --notes-file docs/V24_GITHUB_RELEASE_DRAFT.md
```

## Current Blockers

- `gh` is not available in the local PowerShell/Codex environment.
- Codex shell cannot access remote Git via HTTPS credentials.
- Release was not created in v0.26 automation.

## Claim Boundary

The Release is a public review package. It is not an official GEARS result, leaderboard result, SOTA claim, biological discovery claim, or clinical claim.
