# v0.22 Repository Sanitization Report

## Scope

This audit prepares EvoPrior-AIVC for public GitHub display or mentor review. It checks tracked files, raw data policy, generated outputs, local/private paths, credential-like strings, and internal workflow text.

## Commands

```powershell
git status --short
git ls-files
git ls-files | rg "data/raw|outputs/runs|outputs/release|.venv|__pycache__|.pytest_cache|.ruff_cache|egg-info|.h5ad|.pt|.pkl|.npz|.parquet"
git grep -n -E "<local-path-or-credential-pattern>" -- README.md docs reports configs scripts src tests .github docker
```

## Tracked Raw Data Status

Pass. No raw H5AD, model checkpoint, pickle, NumPy archive, parquet file, or large benchmark data file is tracked.

Tracked raw-data path:

- `data/raw/.gitkeep`

## Tracked Outputs Status

Pass. No generated run output or release bundle directory is tracked.

Tracked output placeholders:

- `outputs/runs/.gitkeep`
- `outputs/release/.gitkeep`

Small reviewer-facing reports under `reports/` are intentionally tracked.

## Local Path Findings

The scan found historical Windows user-specific paths in older GEARS and pytest failure notes. These were generalized in public-facing text to `%APPDATA%`, `%LOCALAPPDATA%`, or generic Windows user-temp wording where the exact username was not needed.

## Secrets Findings

No API keys, passwords, service credentials, or private agent paths were found. Several code hits for credential-adjacent words are ordinary perturbation-label parsing variables and are not credentials.

## Codex/Internal Artifact Findings

`docs/CODEX_HANDOFF.md` remains an internal operational handoff file because the project uses it as durable development context. It is not included in the public README quick links or v0.22 release bundle.

## Actions Taken

- Polished README first screen for external readers.
- Added final public release notes, public demo guide, repository profile copy, and final public checklist.
- Generalized user-specific local paths in public docs/config notes.
- Kept raw data, generated outputs, virtual environments, caches, and Docker artifacts out of tracked files.

## Result

Status: `pass_with_context`.

The repository is ready for public review as a documented release candidate, with the claim boundary preserved: internal GEARS-compatible Norman result only; not official GEARS, not leaderboard-comparable, not SOTA.
