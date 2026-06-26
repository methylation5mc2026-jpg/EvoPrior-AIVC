# v0.23 Showcase Index

This is the recommended reading path for an external reviewer.

| order | file | why it exists | question answered | time |
| ---: | --- | --- | --- | --- |
| 1 | `README.md` | Public front door | What is this project and what is the main result? | 3 min |
| 2 | `docs/V18_RELEASE_MODEL_CARD.md` | Model documentation | What exactly is the validated residual baseline? | 5 min |
| 3 | `docs/V18_BENCHMARK_CARD.md` | Benchmark documentation | What data, split, and metrics define the result? | 5 min |
| 4 | `docs/V17_EXTERNAL_RESULT_CARD.md` | Result card | What are the main metrics and audits? | 4 min |
| 5 | `docs/V22_PUBLIC_DEMO_GUIDE.md` | Reproduction guide | How can I smoke-test or reproduce it? | 5-20 min |
| 6 | `docs/V23_MENTOR_REVIEW_BRIEF.md` | Mentor-facing brief | What should a mentor understand quickly? | 3 min |
| 7 | `docs/V23_PROJECT_PAGE_ASSETS.md` | Website copy | How should this appear on a personal website? | 5 min |
| 8 | `docs/KNOWN_FAILURES.md` | Claim-risk ledger | What is known to be blocked or underpowered? | 8 min |

## Core Evidence Pointers

- Benchmark: Norman/scPerturb `gears_norman_scperturb_v013`
- Data checksum: `c870e6967d91c017d9da827bab183cd6`
- Split status: internal GEARS-compatible, not official GEARS
- Command: `python scripts/run_norman_residual_multiseed.py --config configs/experiment/gears_norman_v017_multiseed_residual.yaml`
- Output: `outputs/runs/v0.17-norman-validated-residual-baseline/gears_norman_scperturb_v013/20260625T100322Z/`
- Commit/tag target for this package: `v0.23-github-publish-or-project-page-assets`

## Claim Boundary

The showcase may present this as a reproducible AI-biology benchmark engineering project with a validated internal GEARS-compatible Norman residual baseline. It must not present it as official GEARS, leaderboard-comparable, SOTA, or biological discovery.
