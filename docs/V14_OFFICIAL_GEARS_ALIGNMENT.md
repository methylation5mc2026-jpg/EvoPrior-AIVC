# v0.14 Official GEARS Alignment

## Decision Summary

Official GEARS execution is blocked in the current environment. v0.14 therefore records a precise official-wrapper blocker and proceeds with a strengthened GEARS-compatible Norman baseline package.

## Feasibility Table

| Item | Status | Evidence | Decision |
| --- | --- | --- | --- |
| `cell-gears` distribution | unavailable | `python -m pip show cell-gears` reports package not found | blocked |
| `gears` distribution/module | unavailable | `python -m pip show gears` reports package not found; `import gears` fails | blocked |
| `torch` | unavailable | `python -m pip show torch` reports package not found; `import torch` fails | blocked |
| `torch_geometric` | unavailable | `python -m pip show torch_geometric` reports package not found | blocked |
| `pip install cell-gears` | blocked | download succeeds, install fails with `WinError 5` writing user site | blocked |
| Norman H5AD data | ready | md5 `c870e6967d91c017d9da827bab183cd6` | usable |
| GEARS-compatible split | ready | v0.13 split plus v0.14 `random_combo` category | run aligned baseline |
| Official split files | not imported | no local official GEARS split artifact | not official |
| Metric compatibility | internal compatible | MAE, MSE, Pearson, Spearman, DE20/DE50 | not leaderboard |

## Blocker

The official/cell-gears stack cannot be installed or imported in the current session. The install attempt:

```powershell
python -m pip install cell-gears
```

downloaded `cell_gears-0.1.2` and `torch-2.12.1`, then failed:

```text
OSError: [WinError 5] Permission denied: C:\Users\HiC3C\AppData\Roaming\Python
```

## Alignment Status

v0.14 can claim:

- public Norman/scPerturb data access is reproducible;
- data checksum is locked;
- split is GEARS-compatible/internal and includes seen0, seen1, seen2, and random_combo categories;
- metrics are GEARS-compatible internal metrics;
- official wrapper blocker is recorded.

v0.14 cannot claim:

- official GEARS result;
- leaderboard comparability;
- SOTA;
- neural GEARS reproduction;
- biological discovery.

## Next Unblock Step

Use a clean environment with writable user/site packages and install a pinned official stack, then rerun:

```powershell
python scripts/run_official_gears_wrapper.py --config configs/experiment/gears_norman_v014_official_wrapper.yaml
```

