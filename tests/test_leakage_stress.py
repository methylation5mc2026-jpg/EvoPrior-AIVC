import pandas as pd

from evoprior_aivc.evaluation.leakage_stress import (
    all_critical_checks_pass,
    run_norman_leakage_stress_checks,
    stress_results_to_frame,
)


def test_norman_leakage_stress_passes_clean_manifest_and_negative_control():
    manifest = _manifest()
    results = run_norman_leakage_stress_checks(
        split_manifest=manifest,
        config=_config(),
        selected_metrics={"mae_delta": 0.4, "mse_delta": 3.0},
        shuffled_target_metrics={"mae_delta": 0.8, "mse_delta": 6.0},
        shuffled_feature_metrics={"mae_delta": 0.7, "mse_delta": 5.0},
    )

    frame = stress_results_to_frame(results)

    assert all_critical_checks_pass(results)
    assert set(frame["check_id"]).issuperset(
        {
            "no_test_combo_in_train_or_val",
            "selection_protocol_uses_validation_not_test",
            "shuffled_target_control_degrades",
            "shuffled_feature_control_degrades",
        }
    )


def test_norman_leakage_stress_flags_combo_leakage():
    manifest = _manifest()
    manifest.loc[manifest["group_id"] == "g_train_combo", "perturbation"] = "C+D"

    results = run_norman_leakage_stress_checks(
        split_manifest=manifest,
        config=_config(),
        selected_metrics={"mae_delta": 0.4, "mse_delta": 3.0},
    )

    frame = stress_results_to_frame(results).set_index("check_id")

    assert not bool(frame.loc["no_test_combo_in_train_or_val", "passed"])


def _manifest() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "group_id": [
                "g_train_single",
                "g_train_combo",
                "g_val_combo",
                "g_test_combo",
            ],
            "split": ["train", "train", "val", "test"],
            "perturbation": ["A", "A+B", "A+C", "C+D"],
            "perturbation_type": ["single", "combo", "combo", "combo"],
            "split_class": ["single_seen", "seen2", "seen1", "seen0"],
        }
    )


def _config() -> dict:
    return {
        "selection": {"split": "val", "metric": "mae_delta"},
        "features": {
            "leakage_policy": (
                "train-only residual fitting; validation-only model selection; "
                "test used once"
            )
        },
    }
