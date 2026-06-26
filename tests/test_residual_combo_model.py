import numpy as np
import pandas as pd

from evoprior_aivc.baselines import (
    DeltaDataset,
    ResidualComboConfig,
    ResidualComboCorrectionBaseline,
    WeightedComboAdditiveBaseline,
)


def test_residual_combo_base_only_matches_base_prediction():
    train = _toy_dataset()
    query = _subset(train, ["A+B"])
    base = WeightedComboAdditiveBaseline(ridge_alpha=0.0).fit(train)
    residual = ResidualComboCorrectionBaseline(
        ResidualComboConfig(
            residual_model="none",
            residual_scale=0.0,
            weighted_ridge_alpha=0.0,
        )
    ).fit(train)

    expected = base.predict_delta(query)
    predicted = residual.predict_delta(query)

    pd.testing.assert_frame_equal(predicted, expected)


def test_residual_combo_predicts_finite_values_and_records_train_vocab():
    train = _toy_dataset()
    query = DeltaDataset(
        group_ids=("A+D",),
        metadata=pd.DataFrame(
            {
                "perturbation": ["A+D"],
                "perturbation_type": ["combo"],
                "perturbation_genes": ["A;D"],
                "cell_type": ["K562"],
                "split_class": ["seen1"],
            },
            index=["A+D"],
        ),
        control_expression=pd.DataFrame([[0.0, 0.0]], index=["A+D"], columns=["g1", "g2"]),
        observed_post_expression=pd.DataFrame([[0.0, 0.0]], index=["A+D"], columns=["g1", "g2"]),
        observed_delta=pd.DataFrame([[0.0, 0.0]], index=["A+D"], columns=["g1", "g2"]),
    )
    model = ResidualComboCorrectionBaseline(
        ResidualComboConfig(residual_model="pca_ridge", pca_components=2, residual_scale=0.5)
    ).fit(train)

    predicted = model.predict_delta(query)

    assert predicted.shape == (1, 2)
    assert np.isfinite(predicted.to_numpy()).all()
    assert "D" not in model.feature_encoder_.gene_vocabulary_
    assert model.manifest()["fit_status"]["fit_mode"] == "pca_ridge"


def test_residual_combo_improves_toy_seen_combo_over_base():
    train = _toy_dataset()
    query = _subset(train, ["A+B", "A+C"])
    base = WeightedComboAdditiveBaseline(ridge_alpha=10.0).fit(train)
    residual = ResidualComboCorrectionBaseline(
        ResidualComboConfig(
            residual_model="ridge",
            residual_scale=1.0,
            alpha=0.0,
            weighted_ridge_alpha=10.0,
        )
    ).fit(train)

    base_error = _mae(query.observed_delta, base.predict_delta(query))
    residual_error = _mae(query.observed_delta, residual.predict_delta(query))

    assert residual_error < base_error


def test_residual_combo_zero_delta_supports_residual_only_ablation():
    train = _toy_dataset()
    query = _subset(train, ["A+B", "A+C"])
    model = ResidualComboCorrectionBaseline(
        ResidualComboConfig(
            base_model="zero_delta",
            residual_model="pca_ridge",
            residual_scale=1.0,
            pca_components=2,
        )
    ).fit(train)

    predicted = model.predict_delta(query)

    assert predicted.shape == query.observed_delta.shape
    assert np.isfinite(predicted.to_numpy()).all()
    assert model.manifest()["config"]["base_model"] == "zero_delta"


def test_residual_combo_shuffle_controls_are_recorded():
    train = _toy_dataset()
    model = ResidualComboCorrectionBaseline(
        ResidualComboConfig(
            residual_model="ridge",
            residual_scale=1.0,
            residual_target_shuffle_seed=10,
            metadata_feature_shuffle_seed=11,
        )
    ).fit(train)

    manifest = model.manifest()["config"]

    assert manifest["residual_target_shuffle_seed"] == 10
    assert manifest["metadata_feature_shuffle_seed"] == 11


def _toy_dataset() -> DeltaDataset:
    metadata = pd.DataFrame(
        {
            "perturbation": ["A", "B", "C", "A+B", "A+C"],
            "perturbation_type": ["single", "single", "single", "combo", "combo"],
            "perturbation_genes": ["A", "B", "C", "A;B", "A;C"],
            "cell_type": ["K562", "K562", "K562", "K562", "K562"],
            "split_class": ["single_seen", "single_seen", "single_seen", "seen2", "seen2"],
        },
        index=["A", "B", "C", "A+B", "A+C"],
    )
    delta = pd.DataFrame(
        [
            [1.0, 0.0],
            [0.0, 1.0],
            [0.5, 0.5],
            [2.5, 1.0],
            [2.0, 0.5],
        ],
        index=metadata.index,
        columns=["g1", "g2"],
    )
    control = pd.DataFrame(0.0, index=metadata.index, columns=delta.columns)
    return DeltaDataset(
        group_ids=tuple(metadata.index),
        metadata=metadata,
        control_expression=control,
        observed_post_expression=delta,
        observed_delta=delta,
    )


def _subset(dataset: DeltaDataset, ids: list[str]) -> DeltaDataset:
    return DeltaDataset(
        group_ids=tuple(ids),
        metadata=dataset.metadata.loc[ids],
        control_expression=dataset.control_expression.loc[ids],
        observed_post_expression=dataset.observed_post_expression.loc[ids],
        observed_delta=dataset.observed_delta.loc[ids],
    )


def _mae(observed: pd.DataFrame, predicted: pd.DataFrame) -> float:
    return float(np.mean(np.abs(observed.to_numpy(dtype=float) - predicted.to_numpy(dtype=float))))
