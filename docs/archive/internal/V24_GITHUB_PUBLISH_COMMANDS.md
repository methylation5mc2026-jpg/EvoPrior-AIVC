# v0.24 GitHub Publish Commands

These commands are owner-side commands. They are not executed automatically in v0.24 because this environment has no configured `origin`, no `gh` on `PATH`, and no explicit push approval.

## Preflight

```powershell
cd C:\Users\HiC3C\Documents\AIVC
git status --short
git branch --show-current
git tag --points-at HEAD
git remote -v
```

Expected before publish:

- branch: `feat/github-push-release-website-v024`
- working tree: clean
- tag at HEAD after commit: `v0.24-github-push-and-release-or-website-integration`
- no raw data, outputs, caches, or virtual environments staged

## Add Remote If Needed

```powershell
git remote add origin <repo-url>
git remote -v
```

## Push Branch And Tag

```powershell
git push -u origin feat/github-push-release-website-v024
git push origin v0.24-github-push-and-release-or-website-integration
```

## Create Release Manually In GitHub UI

1. Open the repository on GitHub.
2. Go to Releases.
3. Draft a new release.
4. Choose tag `v0.24-github-push-and-release-or-website-integration`.
5. Paste the body from `docs/V24_GITHUB_RELEASE_DRAFT.md`.
6. Do not upload raw data or generated benchmark outputs.

## Optional `gh` Path

Use only after installing and authenticating GitHub CLI:

```powershell
gh auth status
gh release create v0.24-github-push-and-release-or-website-integration --title "EvoPrior-AIVC v0.24: Public Review Package and Website Integration Assets" --notes-file docs/V24_GITHUB_RELEASE_DRAFT.md
```
