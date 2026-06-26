# v0.24 Public Link Audit

## Current Status

No public GitHub remote is configured in this checkout, and no website update was performed in v0.24. Public links therefore remain pending until the owner creates or connects the repository and publishes the website page.

## Local Link Checks

| Item | Status | Note |
| --- | --- | --- |
| `git remote -v` | pending | no output; `origin` is not configured |
| `gh --version` | blocked | `gh` not on `PATH` |
| GitHub Release URL | pending | requires pushed tag |
| Personal website URL | pending | no website repo edited in v0.24 |
| Local Windows paths in public docs | review required | keep local paths out of final website copy |

## Links To Fill After Publish

| Link | Value |
| --- | --- |
| GitHub repository | `<pending>` |
| GitHub release | `<pending>` |
| v0.24 tag | `<pending>` |
| Project website page | `<pending>` |
| Release bundle location | local ignored path `outputs/release/v0.24/20260626T024343Z/` |

## Audit Rules

- Public pages should link to repository files, not local `C:\Users\...` paths.
- Benchmark result links must point to docs or reports, not raw local outputs unless the output artifact is intentionally public.
- Any public metric table must include `internal GEARS-compatible, not official GEARS`.
- Any release body must keep the forbidden-claims list.
