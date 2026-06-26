# v0.17 Ablation And Leakage Audit

## Artifacts

- Output: `outputs/runs/v0.17-norman-validated-residual-baseline/gears_norman_scperturb_v013/20260625T100322Z/`
- Ablation metrics: `ablation_metrics.csv`
- Ablation summary: `ablation_summary.csv`
- Ablation report: `ablation_report.md`
- Leakage checks: `leakage_stress_checks.csv`
- Leakage report: `leakage_stress_report.md`

## Ablation Result

Validation-selected ablation winner: `pca_ridge_residual_only`.

Selection rule: mean validation MAE across seeds; test metrics are reported after the rule is fixed.

Primary v0.17 model remains the frozen v0.16 family `weighted_pca_ridge_s075_a10`. The residual-only ablation is a follow-up candidate, not an official GEARS or leaderboard result.

## Negative Controls

| control | test MAE mean | test MSE mean | status |
| --- | ---: | ---: | --- |
| selected primary | 0.430778 | 3.668870 | reference |
| shuffled residual target | 0.598936 | 8.050228 | degraded |
| shuffled perturbation features | 0.584434 | 7.413003 | degraded |

## Leakage Stress

All critical stress checks passed:

- no test combo appears in train or validation as a combo target;
- train, validation, and test group IDs are disjoint;
- model selection uses validation metrics, not test metrics;
- perturbation labels do not encode split class tokens;
- split manifest contains train/val/test and expected GEARS-compatible classes;
- feature policy documents train-only residual fitting, validation-only selection, and one-time test evaluation;
- shuffled-target and shuffled-feature controls degrade relative to the selected model.

## Official GEARS Recheck

Dry-run command:

```powershell
python scripts/run_official_gears_wrapper.py --config configs/experiment/gears_norman_v014_official_wrapper.yaml --dry-run
```

Output: `outputs/runs/v0.14-official-gears-wrapper-blocked/gears_norman_scperturb_v013/20260625T100234Z/`.

Status: `document_blocker`; this remains a feasibility artifact, not an official GEARS run.
