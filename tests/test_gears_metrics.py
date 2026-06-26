import pandas as pd

from evoprior_aivc.baselines.base import DeltaDataset
from evoprior_aivc.evaluation.gears_metrics import (
    per_class_metrics,
    per_perturbation_metrics,
)


def test_gears_metric_tables_are_grouped():
    dataset = DeltaDataset(
        group_ids=("g1", "g2"),
        metadata=pd.DataFrame(
            {
                "perturbation": ["A+B", "C+D"],
                "perturbation_type": ["combo", "combo"],
                "split_class": ["seen2", "seen0"],
            },
            index=["g1", "g2"],
        ),
        control_expression=pd.DataFrame(
            [[0.0, 0.0], [0.0, 0.0]],
            index=["g1", "g2"],
            columns=["x", "y"],
        ),
        observed_post_expression=pd.DataFrame(
            [[1.0, 1.0], [2.0, 2.0]],
            index=["g1", "g2"],
            columns=["x", "y"],
        ),
        observed_delta=pd.DataFrame(
            [[1.0, 1.0], [2.0, 2.0]],
            index=["g1", "g2"],
            columns=["x", "y"],
        ),
    )
    predicted = dataset.observed_delta.copy()

    per_pert = per_perturbation_metrics(dataset, predicted)
    per_class = per_class_metrics(dataset, predicted)

    assert set(per_pert["perturbation"]) == {"A+B", "C+D"}
    assert {"seen2", "seen0"}.issubset(set(per_class["group_value"]))
