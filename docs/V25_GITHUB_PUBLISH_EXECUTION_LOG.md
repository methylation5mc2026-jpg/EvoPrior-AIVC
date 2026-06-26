# v0.25 GitHub Publish Execution Log

## Objective

Turn the v0.24 local release-ready package into a GitHub-presentable project, or generate an exact manual publication package if automation cannot push.

## Inputs

- Local branch: `feat/github-publish-execution-v025`
- Completed source tag: `v0.24-github-push-and-release-or-website-integration`
- Intended GitHub repository: `https://github.com/methylation5mc2026-jpg/EvoPrior-AIVC`
- Release tag to publish: `v0.24-github-push-and-release-or-website-integration`
- v0.25 target tag: `v0.25-github-publish-execution-and-final-link-package`

## Remote Audit

| Question | Result |
| --- | --- |
| Is `origin` configured? | No |
| Provided target URL | `https://github.com/methylation5mc2026-jpg/EvoPrior-AIVC.git` |
| Could Codex add `origin`? | No |
| Failure | `.git/config: Permission denied` |
| Is `gh` installed? | No, command not found |
| Is `gh` authenticated? | Not checkable |
| Is current branch safe to push? | Yes after owner adds remote; working tree was clean at branch start |
| Are tags available? | Yes, v0.24 tag is at HEAD before v0.25 docs |
| User permission to publish? | User provided the target GitHub URL and stated the result is ready to publish |

## Decision

Manual commands only from this environment. Publishing is authorized by user intent, but local automation cannot write `.git/config`, cannot create `.git` locks reliably, and cannot use GitHub CLI.

## What Was Not Executed

- `git remote add origin ...`
- `git push`
- `gh release create`
- GitHub-hosted CI check
- Website update

## Verification

| Check | Result |
| --- | --- |
| Plain `python -m pytest` | failed due host Windows Temp permission |
| Repo-local pytest before edits | `164 passed, 4 warnings` |
| Release smoke | `pass`, `outputs/runs/v0.19-release-smoke/20260626T031329Z/` |
| Artifact check | `pass`, `reports/v0.24_artifact_manifest.md` |
| Final repo-local pytest | `164 passed, 4 warnings` |
| Targeted ruff | not needed, docs-only v0.25 change |

## Claim Boundary

v0.25 is a final GitHub publish execution package and link package. It is not a new benchmark run and does not change the v0.17 model, split, metrics, or official GEARS status.
