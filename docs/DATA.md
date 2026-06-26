# Data Policy And Acquisition

## Required Public Dataset

```text
NormanWeissman2019_filtered.h5ad
```

Source: scPerturb Zenodo record 13350497, version 1.4.

Expected local path:

```text
data/raw/NormanWeissman2019_filtered.h5ad
```

Expected md5:

```text
c870e6967d91c017d9da827bab183cd6
```

## Verify Access Instructions

```powershell
python scripts/prepare_gears_norman.py --config configs/data/gears_norman_v013.yaml --dry-run
```

## Verify Checksum

```powershell
Get-FileHash data/raw/NormanWeissman2019_filtered.h5ad -Algorithm MD5
```

The `Hash` field should equal `c870e6967d91c017d9da827bab183cd6`.

## What Is Not Committed

- raw H5AD files
- generated run outputs
- generated data reports
- generated release bundles
- virtual environments
- cache directories

Tracked `data/` and `outputs/` directories contain placeholders only.

## Claim Boundary

This data guide supports reproducibility. It does not provide official GEARS alignment, leaderboard comparability, SOTA evidence, biological discovery, or clinical evidence.
