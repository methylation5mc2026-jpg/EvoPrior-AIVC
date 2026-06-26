# v0.24 GitHub Publish Status

## Decision

v0.24 prepares the final publishing layer but does not push to GitHub or create a GitHub Release from this environment.

## Local Audit

| Check | Result |
| --- | --- |
| Branch | `feat/github-push-release-website-v024` |
| Rollback tag | `v0.23-github-publish-or-project-page-assets` |
| Git remote | no `origin` configured |
| GitHub CLI | `gh` is not installed or not on `PATH` |
| Direct push allowed | no |
| GitHub Release creation allowed | no |
| Website update performed | no |

## Local Verification

| Check | Result |
| --- | --- |
| Targeted tests | `7 passed, 2 warnings` |
| Targeted ruff | passed |
| Release bundle | `outputs/release/v0.24/20260626T024343Z/` |
| Artifact manifest | `reports/v0.24_artifact_manifest.md`, status `pass` |
| Release smoke | `outputs/runs/v0.19-release-smoke/20260626T024213Z/`, status `pass` |
| Full pytest | `164 passed, 4 warnings` |
| Diff check | passed |

## What v0.24 Adds

- GitHub publish commands for the project owner.
- GitHub Release draft text with the current claim boundary.
- Website/project-page copy that can be pasted into a personal site.
- Public link audit checklist before and after publishing.
- Final presentation summary for mentor or external reviewer use.

## Claim Boundary

Allowed: a publish-ready repository package around the validated v0.17 internal GEARS-compatible Norman residual baseline.

Forbidden: official GEARS, leaderboard comparability, SOTA, biological discovery, clinical claim, general model superiority, or a claim that GitHub/website publishing already happened.

## Next Gate

The owner must configure a remote and explicitly approve push/release execution before any publish action:

```powershell
git remote add origin <repo-url>
git push -u origin feat/github-push-release-website-v024
git push origin v0.24-github-push-and-release-or-website-integration
```
