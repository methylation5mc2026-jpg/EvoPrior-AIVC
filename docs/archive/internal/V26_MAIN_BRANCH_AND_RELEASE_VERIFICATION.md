# v0.26 Main Branch And Release Verification

## Summary

The GitHub repository exists and the complete project is public on `feat/github-publish-execution-v025`. The default repository root currently opens on `main`, which has only minimal bootstrap files and one commit. v0.26 should merge the complete project branch into `main` before the root URL is used as the primary mentor/application link.

## Repository

- URL: `https://github.com/methylation5mc2026-jpg/EvoPrior-AIVC`
- Visibility: public
- Default branch observed in browser: `main`
- Full project branch: `feat/github-publish-execution-v025`
- v0.25 commit: `263b1c3`
- v0.25 tag: `v0.25-github-publish-execution-and-final-link-package`

## Remote Audit

| Item | Status |
| --- | --- |
| Local remote | `origin -> https://github.com/methylation5mc2026-jpg/EvoPrior-AIVC.git` |
| Remote access from Codex shell | blocked by `schannel: AcquireCredentialsHandle failed: SEC_E_NO_CREDENTIALS` |
| Browser repo root | public, default branch `main`, minimal files |
| Browser feature branch | public, complete project tree with docs/configs/src/tests |
| Releases page | no releases |
| Actions page | `ci` workflow visible, one run for commit `263b1c3`; status not fully readable from unauthenticated browser page |
| `gh` CLI | unavailable on PATH |

## Local Verification

| Command | Result |
| --- | --- |
| `python scripts/run_release_smoke.py --config configs/experiment/release_smoke_v019.yaml` | passed; wrote `outputs/runs/v0.19-release-smoke/20260626T033407Z/` |
| `python scripts/check_release_artifacts.py` | passed; refreshed `reports/v0.24_artifact_manifest.json` |
| `python -m pytest -p no:cacheprovider --basetemp .tmp_pytest_v26` | `164 passed, 4 warnings` |
| `git diff --check` | passed with only expected LF-to-CRLF warnings |

Plain `python -m pytest` can fail on this Windows host because pytest cannot create its default `%LOCALAPPDATA%\Temp\pytest-of-<user>` directory. The repo-local `--basetemp` command above is the validated workaround.

## Recommended Action

Preferred: merge `feat/github-publish-execution-v025` into `main` and push `main`, so `https://github.com/methylation5mc2026-jpg/EvoPrior-AIVC` shows the full project.

Safe owner-side command path:

```powershell
cd C:\Users\HiC3C\Documents\AIVC
git fetch origin main
git switch -c main origin/main
git merge --no-ff feat/github-publish-execution-v025 -m "merge: publish EvoPrior-AIVC public review package"
python scripts/run_release_smoke.py --config configs/experiment/release_smoke_v019.yaml
python -m pytest -p no:cacheprovider --basetemp .tmp_pytest_main
git push origin main
```

If `main` already exists locally:

```powershell
git switch main
git pull origin main
git merge --no-ff feat/github-publish-execution-v025 -m "merge: publish EvoPrior-AIVC public review package"
git push origin main
```

If merge is blocked or uncomfortable, open this PR instead:

`https://github.com/methylation5mc2026-jpg/EvoPrior-AIVC/pull/new/feat/github-publish-execution-v025`

## Claim Boundary

No scientific claim changes in v0.26. The result remains an internal GEARS-compatible Norman baseline, not official GEARS, not leaderboard-comparable, and not SOTA.
