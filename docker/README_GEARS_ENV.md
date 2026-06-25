# GEARS Environment Route

This folder documents a conservative Docker route for official GEARS dependency unblocking.

## Build

```powershell
docker build -f docker/Dockerfile.gears -t evoprior-gears-env .
```

## Import Check

```powershell
docker run --rm evoprior-gears-env python -c "import torch; import torch_geometric; import gears; print('ok')"
```

## Scope

The Dockerfile is an environment recipe. It does not include raw Norman data, does not import official split files, does not train official GEARS, and does not produce official GEARS metrics.

## Next Manual Action

After the import check succeeds, implement a separate official GEARS train/evaluate wrapper that matches official preprocessing, split files, and metrics exactly. Only then can the project discuss official GEARS alignment.
