import pandas as pd

from evoprior_aivc.baselines.base import DeltaDataset
from evoprior_aivc.baselines.combo_additive import SingleEffectAdditiveComboBaseline


def test_combo_additive_sums_seen_single_effects():
    train = DeltaDataset(
        group_ids=("A", "B"),
        metadata=pd.DataFrame(
            {
                "perturbation": ["A", "B"],
                "perturbation_type": ["single", "single"],
                "perturbation_genes": ["A", "B"],
            },
            index=["A", "B"],
        ),
        control_expression=pd.DataFrame(
            [[0.0, 0.0], [0.0, 0.0]],
            index=["A", "B"],
            columns=["g1", "g2"],
        ),
        observed_post_expression=pd.DataFrame(
            [[1.0, 2.0], [3.0, 5.0]],
            index=["A", "B"],
            columns=["g1", "g2"],
        ),
        observed_delta=pd.DataFrame(
            [[1.0, 2.0], [3.0, 5.0]],
            index=["A", "B"],
            columns=["g1", "g2"],
        ),
    )
    query = DeltaDataset(
        group_ids=("A+B",),
        metadata=pd.DataFrame(
            {
                "perturbation": ["A+B"],
                "perturbation_type": ["combo"],
                "perturbation_genes": ["A;B"],
            },
            index=["A+B"],
        ),
        control_expression=pd.DataFrame([[0.0, 0.0]], index=["A+B"], columns=["g1", "g2"]),
        observed_post_expression=pd.DataFrame([[0.0, 0.0]], index=["A+B"], columns=["g1", "g2"]),
        observed_delta=pd.DataFrame([[0.0, 0.0]], index=["A+B"], columns=["g1", "g2"]),
    )

    baseline = SingleEffectAdditiveComboBaseline().fit(train)
    predicted = baseline.predict_delta(query)

    assert predicted.loc["A+B", "g1"] == 4.0
    assert predicted.loc["A+B", "g2"] == 7.0
    assert baseline.prediction_fallbacks()["fallback_mode"].iloc[0] == "all_single_effects"
