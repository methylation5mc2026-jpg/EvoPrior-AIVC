# Datasets

## Norman/scPerturb

| field | value |
| --- | --- |
| File | `NormanWeissman2019_filtered.h5ad` |
| Source | scPerturb Zenodo record 13350497, version 1.4 |
| Expected md5 | `c870e6967d91c017d9da827bab183cd6` |
| Local path | `data/raw/NormanWeissman2019_filtered.h5ad` |
| Status | required for full reproduction; not committed |

## Local Verification

```powershell
python scripts/prepare_gears_norman.py --config configs/data/gears_norman_v013.yaml --dry-run
Get-FileHash data/raw/NormanWeissman2019_filtered.h5ad -Algorithm MD5
```

## Data Policy

The repository tracks placeholder directories only. Raw H5AD files, generated outputs, and local caches must remain untracked.

See `docs/DATA.md` for the stable public data guide.
