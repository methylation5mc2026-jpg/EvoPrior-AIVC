# v0.25 Public URL Placeholder Audit

## Known Target URLs

| Item | URL | Status |
| --- | --- | --- |
| GitHub repository | `https://github.com/methylation5mc2026-jpg/EvoPrior-AIVC` | intended, pending owner push |
| v0.24 release | `https://github.com/methylation5mc2026-jpg/EvoPrior-AIVC/releases/tag/v0.24-github-push-and-release-or-website-integration` | pending owner release creation |
| README | `https://github.com/methylation5mc2026-jpg/EvoPrior-AIVC#readme` | pending owner push |
| Model card | `https://github.com/methylation5mc2026-jpg/EvoPrior-AIVC/blob/feat/github-publish-execution-v025/docs/V18_RELEASE_MODEL_CARD.md` | pending owner push |
| Benchmark card | `https://github.com/methylation5mc2026-jpg/EvoPrior-AIVC/blob/feat/github-publish-execution-v025/docs/V18_BENCHMARK_CARD.md` | pending owner push |
| Reproducibility runbook | `https://github.com/methylation5mc2026-jpg/EvoPrior-AIVC/blob/feat/github-publish-execution-v025/docs/V18_REPRODUCIBILITY_RUNBOOK.md` | pending owner push |
| Project website page | `<PROJECT_PAGE_URL>` | unknown |

## Scan Result

Pattern scan found these classes:

| Class | Hits | Decision |
| --- | --- | --- |
| `docs/CODEX_HANDOFF.md` historical `.git/index.lock` notes | multiple | internal note, acceptable |
| `docs/KNOWN_FAILURES.md` `.git/index.lock` note | one | internal note, acceptable |
| `docs/V14_OFFICIAL_GEARS_ALIGNMENT.md` `%APPDATA%` permission note | one | blocker evidence, acceptable |
| `docs/V18_REPRODUCIBILITY_RUNBOOK.md` `.git/index.lock` note | one | troubleshooting note, acceptable |
| `docs/V23_GITHUB_PUBLISH_GUIDE.md` `<YOUR_GITHUB_REPO_URL>` | one | acceptable template placeholder |
| `docs/V23_PROJECT_PAGE_ASSETS.md` `<YOUR_GITHUB_REPO_URL>` | one | should be replaced when website page is edited |
| `docs/V24_GITHUB_PUBLISH_COMMANDS.md` local PowerShell path | one | internal command note, acceptable |
| `docs/V24_PUBLIC_LINK_AUDIT.md` local-path warning | one | warning text, acceptable |

## Must Replace Before Public Website

- Replace `<PROJECT_PAGE_URL>` with the actual personal website URL after the website page exists.
- Replace `<YOUR_GITHUB_REPO_URL>` in copied website/project-page text with `https://github.com/methylation5mc2026-jpg/EvoPrior-AIVC`.

## Safe To Keep In Repository

- Historical `.git/index.lock` notes in `docs/CODEX_HANDOFF.md`.
- Reproducibility troubleshooting notes.
- Command-guide placeholders that are clearly marked as templates.

## Public Claim Rule

Every public link package must say that the result is an internal GEARS-compatible Norman baseline, not official GEARS, not leaderboard-comparable, and not SOTA.
