import pandas as pd

from evoprior_aivc.baselines.base import DeltaDataset
from evoprior_aivc.baselines.combo_weighted import WeightedComboAdditiveBaseline


def test_weighted_combo_additive_fits_train_combo_weights():
    train = DeltaDataset(
        group_ids=("A", "B", "A+B"),
        metadata=pd.DataFrame(
            {
                "perturbation": ["A", "B", "A+B"],
                "perturbation_type": ["single", "single", "combo"],
                "perturbation_genes": ["A", "B", "A;B"],
            },
            index=["A", "B", "A+B"],
        ),
        control_expression=pd.DataFrame(
            [[0.0], [0.0], [0.0]],
            index=["A", "B", "A+B"],
            columns=["g1"],
        ),
        observed_post_expression=pd.DataFrame(
            [[1.0], [2.0], [6.0]],
            index=["A", "B", "A+B"],
            columns=["g1"],
        ),
        observed_delta=pd.DataFrame(
            [[1.0], [2.0], [6.0]],
            index=["A", "B", "A+B"],
            columns=["g1"],
        ),
    )
    query = DeltaDataset(
        group_ids=("A+B",),
        metadata=train.metadata.loc[["A+B"]],
        control_expression=train.control_expression.loc[["A+B"]],
        observed_post_expression=train.observed_post_expression.loc[["A+B"]],
        observed_delta=train.observed_delta.loc[["A+B"]],
    )

    baseline = WeightedComboAdditiveBaseline(ridge_alpha=0.0).fit(train)
    predicted = baseline.predict_delta(query)

    assert predicted.loc["A+B", "g1"] > 3.0
    assert "weighted_combo" in baseline.prediction_fallbacks()["fallback_mode"].iloc[0]
