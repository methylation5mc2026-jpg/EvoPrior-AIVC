# v0.20 Official GEARS Docker / WSL Environment

## Current Status

Official GEARS remains `import_ok_run_blocked`. The project has dependency import evidence from `.venv_gears`, but the repository wrapper is still feasibility-only: it does not train/evaluate official GEARS, import official split files, or produce official GEARS metrics.

## Docker Route

Dockerfile: `docker/Dockerfile.gears`

Build:

```powershell
docker build -f docker/Dockerfile.gears -t evoprior-gears-env .
```

Import check:

```powershell
docker run --rm evoprior-gears-env python -c "import torch; import torch_geometric; import gears; print('ok')"
```

This Dockerfile is an environment recipe. It is not a claimed tested official reproduction unless the build and import check are actually run and recorded.

## WSL Route

Use WSL2 or Docker when possible because PyTorch/PyG installation is less fragile in a Linux-like environment than in the current Windows user-site setup.

Recommended next manual action:

1. Build the Docker image or create an equivalent WSL Python environment.
2. Confirm `torch`, `torch_geometric`, and `gears` import together.
3. Import official GEARS Norman split files and preprocessing.
4. Implement a separate official GEARS train/evaluate wrapper.
5. Only compare to official GEARS after exact split and metric alignment.

## Diagnostic Command

```powershell
python scripts/diagnose_official_gears.py
```

Output pattern:

```text
outputs/runs/v0.20-official-gears-diagnostics/<timestamp>/
```

Latest local output:

```text
outputs/runs/v0.20-official-gears-diagnostics/20260625T230451Z/
```

Latest local status: `import_ok_run_blocked`.

## Relation To Earlier Blockers

- v0.14 documented missing dependencies and Windows install permission failures.
- v0.18 documented `.venv_gears` import readiness but wrapper-level official execution remained blocked.
- v0.20 provides a Docker/WSL path without claiming official GEARS execution.

## Claim Boundary

This is environment unblocking work only. It is not an official GEARS result, leaderboard-comparable result, SOTA result, or biological discovery.
