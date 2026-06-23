import numpy as np
import pytest

from evoprior_aivc.baselines import (
    AdditiveBaseline,
    ControlMeanBaseline,
    HierarchicalAdditiveBaseline,
    MeanDeltaBaseline,
    NoChangeBaseline,
    PerturbationMeanDeltaBaselineV2,
    RidgeBaseline,
    RidgeCVBaseline,
    build_delta_dataset,
)
from evoprior_aivc.data.pseudobulk import aggregate_pseudobulk
from evoprior_aivc.data.synthetic import make_synthetic_perturbation_adata
from evoprior_aivc.evaluation.metrics import mean_absolute_error


def _synthetic_delta_dataset(seed: int = 0):
    adata = make_synthetic_perturbation_adata(seed=seed, cells_per_group=8)
    expression, metadata = aggregate_pseudobulk(adata)
    return build_delta_dataset(expression, metadata)


@pytest.mark.parametrize(
    "baseline",
    [
        NoChangeBaseline(),
        MeanDeltaBaseline(),
        AdditiveBaseline(),
        RidgeBaseline(alpha=1.0),
        ControlMeanBaseline(),
        PerturbationMeanDeltaBaselineV2(),
        HierarchicalAdditiveBaseline(alpha=2.0),
        RidgeCVBaseline(alphas=(0.01, 0.1, 1.0)),
    ],
)
def test_baselines_fit_and_predict_finite_delta(baseline):
    dataset = _synthetic_delta_dataset(seed=1)

    baseline.fit(dataset)
    predictions = baseline.predict_delta(dataset)

    assert predictions.shape == dataset.observed_delta.shape
    assert np.isfinite(predictions.to_numpy()).all()


def test_no_change_baseline_predicts_zero_delta():
    dataset = _synthetic_delta_dataset(seed=2)

    predictions = NoChangeBaseline().fit(dataset).predict_delta(dataset)

    assert np.allclose(predictions.to_numpy(), 0.0)


def test_control_mean_baseline_predicts_zero_delta_and_records_fallbacks():
    dataset = _synthetic_delta_dataset(seed=12)

    baseline = ControlMeanBaseline().fit(dataset)
    predictions = baseline.predict_delta(dataset)

    assert np.allclose(predictions.to_numpy(), 0.0)
    assert ("cell_type",) in baseline.available_fallbacks_


def test_mean_delta_baseline_recovers_simple_perturbation_effect():
    dataset = _synthetic_delta_dataset(seed=3)

    predictions = MeanDeltaBaseline().fit(dataset).predict_delta(dataset)
    pert_a_predictions = predictions.loc[dataset.metadata["perturbation"] == "pert_a"]

    assert pert_a_predictions["GENE03"].mean() == pytest.approx(2.0, abs=0.15)


def test_mean_delta_baseline_uses_global_fallback_for_unseen_perturbation():
    dataset = _synthetic_delta_dataset(seed=4)
    train_mask = dataset.metadata["perturbation"] != "pert_c"
    train = _subset_dataset(dataset, train_mask)
    query = _subset_dataset(dataset, ~train_mask)

    baseline = MeanDeltaBaseline(fallback="global").fit(train)
    predictions = baseline.predict_delta(query)

    expected = train.observed_delta.mean(axis=0).to_numpy(dtype=float)
    np.testing.assert_allclose(predictions.iloc[0].to_numpy(dtype=float), expected)


def test_perturbation_mean_delta_v2_global_fallback_for_unseen_perturbation():
    dataset = _synthetic_delta_dataset(seed=13)
    train_mask = dataset.metadata["perturbation"] != "pert_c"
    train = _subset_dataset(dataset, train_mask)
    query = _subset_dataset(dataset, ~train_mask)

    baseline = PerturbationMeanDeltaBaselineV2(fallback="global").fit(train)
    predictions = baseline.predict_delta(query)

    expected = train.observed_delta.mean(axis=0).to_numpy(dtype=float)
    np.testing.assert_allclose(predictions.iloc[0].to_numpy(dtype=float), expected)


def test_hierarchical_additive_shrinkage_reduces_rare_effect_magnitude():
    dataset = _synthetic_delta_dataset(seed=14)
    weak_shrinkage = HierarchicalAdditiveBaseline(alpha=0.0).fit(dataset)
    strong_shrinkage = HierarchicalAdditiveBaseline(alpha=100.0).fit(dataset)
    effect_key = "pert_a"
    weak_norm = np.linalg.norm(
        weak_shrinkage.effect_tables_["perturbation"].loc[effect_key].to_numpy(dtype=float)
    )
    strong_norm = np.linalg.norm(
        strong_shrinkage.effect_tables_["perturbation"].loc[effect_key].to_numpy(dtype=float)
    )

    assert strong_norm < weak_norm


def test_ridge_cv_selects_alpha_and_predicts_shape():
    dataset = _synthetic_delta_dataset(seed=15)

    baseline = RidgeCVBaseline(alphas=(0.01, 0.1, 1.0)).fit(dataset)
    predictions = baseline.predict_delta(dataset)

    assert baseline.selected_alpha_ in {0.01, 0.1, 1.0}
    assert predictions.shape == dataset.observed_delta.shape


def test_ridge_can_overfit_tiny_deterministic_subset():
    dataset = _synthetic_delta_dataset(seed=5)
    tiny = _subset_dataset(dataset, dataset.metadata["perturbation"] == "pert_c")

    baseline = RidgeBaseline(alpha=1e-10).fit(tiny)
    predictions = baseline.predict_delta(tiny)

    assert mean_absolute_error(tiny.observed_delta.to_numpy(), predictions.to_numpy()) < 1e-3


def _subset_dataset(dataset, mask):
    from evoprior_aivc.baselines.base import DeltaDataset

    mask = np.asarray(mask, dtype=bool)
    index = dataset.metadata.index[mask]
    return DeltaDataset(
        group_ids=tuple(index),
        metadata=dataset.metadata.loc[index],
        control_expression=dataset.control_expression.loc[index],
        observed_post_expression=dataset.observed_post_expression.loc[index],
        observed_delta=dataset.observed_delta.loc[index],
    )
