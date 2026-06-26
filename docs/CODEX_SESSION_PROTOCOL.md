# Codex Session Protocol

Status: durable operating notes for rescue and milestone continuation threads.

Rules:

- Reconstruct state from the repository before implementation.
- Keep `docs/CODEX_HANDOFF.md` updated after major loops.
- Do not discard unstaged work or run `git reset --hard`.
- Do not commit raw data, generated outputs, caches, or egg-info directories.
- Keep claims tied to `docs/EXPERIMENT_LEDGER.md`.
- Preserve rollback tags for each milestone.

v0.8 specific boundary:

- HGNC metadata is a real source but not an evolutionary/conservation source.
- Do not claim real evolutionary-prior benefit unless orthology/conservation/gene-age features are configured and supported by ablation.

v0.9 specific boundary:

- `EvoPriorAdditiveModel` is transparent and non-neural.
- Kang v0.9 results are project-split-specific.
- Do not attribute integrated additive gains to HGNC metadata alone when the no-gene-prior additive variant is comparable or better.
