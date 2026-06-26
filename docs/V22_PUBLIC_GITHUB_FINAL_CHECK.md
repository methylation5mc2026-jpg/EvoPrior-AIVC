# v0.22 Public GitHub Final Check

| Check | Status | Evidence or action |
| --- | --- | --- |
| README first screen clear | pass | v0.22 README includes title, summary, badges, key result table, quick links, quickstart, and claim boundary. |
| No raw data tracked | pass | `git ls-files` shows only `data/raw/.gitkeep` under raw data. |
| No heavy outputs tracked | pass | `outputs/runs/.gitkeep` and `outputs/release/.gitkeep` are tracked; generated run and bundle directories are ignored. |
| No credential material | pass | No API keys, passwords, service credentials, or private agent paths found. |
| No personal local paths in public docs | pass_with_context | User-specific Windows paths were generalized; `docs/CODEX_HANDOFF.md` remains internal operational context and is not in public quick links. |
| License present | pass | `LICENSE` |
| Citation present | pass | `CITATION.cff` |
| Contributing present | pass | `CONTRIBUTING.md` |
| Security policy present | pass | `SECURITY.md` |
| CI workflow present | pass | `.github/workflows/ci.yml` |
| Release notes present | pass | `docs/V22_GITHUB_RELEASE_NOTES_FINAL.md` |
| Model card present | pass | `docs/V18_RELEASE_MODEL_CARD.md` |
| Benchmark card present | pass | `docs/V18_BENCHMARK_CARD.md` |
| Data guide present | pass | `docs/V21_PUBLIC_DATA_ACQUISITION_GUIDE.md` |
| Demo guide present | pass | `docs/V22_PUBLIC_DEMO_GUIDE.md` |
| Known limitations present | pass | README, model card, benchmark card, release notes, and known failures docs. |
| Claim boundary present | pass | README and `docs/CLAIMS_AND_EVIDENCE.md`. |
| v0.22 release bundle generated | pass | `outputs/release/v0.22/20260626T000119Z/` |
| v0.22 artifact manifest passed | pass | `reports/v0.22_artifact_manifest.md` |
| Release smoke passed | pass | `outputs/runs/v0.19-release-smoke/20260626T000135Z/` |

## Final Claim Boundary

The repository can publicly claim a reproducible, documented release candidate around a validated residual baseline on a public Norman/scPerturb GEARS-compatible internal split.

It must not claim official GEARS, leaderboard comparability, SOTA, biological discovery, clinical use, or general model superiority.
