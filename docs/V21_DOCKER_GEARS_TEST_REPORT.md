# v0.21 Docker GEARS Test Report

## Summary

Status: `unavailable_docker`.

Docker was not available in the current Windows PowerShell environment, so the v0.21 milestone records an exact blocker rather than claiming a container build or official GEARS reproduction.

## Commands Run

```powershell
docker --version
docker info
```

## Observed Result

Both commands failed with:

```text
docker : The term 'docker' is not recognized as the name of a cmdlet, function, script file, or operable program.
```

## Impact

- `docker/Dockerfile.gears` remains an environment recipe.
- No Docker image was built in this run.
- No container import check was completed in this run.
- No official GEARS training, evaluation, official split import, or official metric output was produced.

The separate non-Docker diagnostic command `python scripts/diagnose_official_gears.py` wrote `outputs/runs/v0.20-official-gears-diagnostics/20260625T233312Z/` with status `import_ok_run_blocked`. This does not change the Docker status.

## Next Manual Action

1. Install Docker Desktop or use WSL2 with Docker available on PATH.
2. Run:

```powershell
docker build -f docker/Dockerfile.gears -t evoprior-gears-env:v0.21 .
docker run --rm evoprior-gears-env:v0.21 python -c "import gears; print('gears import ok')"
```

3. If import succeeds, record package versions and then implement a separate official GEARS train/evaluate wrapper with official split and metrics.

## Claim Boundary

This report documents environment availability only. It is not an official GEARS result, not leaderboard-comparable, not SOTA, and not biological discovery.
