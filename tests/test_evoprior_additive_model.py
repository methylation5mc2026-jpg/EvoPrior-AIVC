import numpy as np
import pandas as pd

from evoprior_aivc.baselines.base import DeltaDataset
from evoprior_aivc.evaluation.metrics import mean_absolute_error
from evoprior_aivc.models import EvoPriorAdditiveModel
from evoprior_aivc.priors.cell_lineage import LineageTree
from evoprior_aivc.priors.gene_prior_table import GenePriorTable


def test_evoprior_additive_shape_finite_and_component_sum():
    train, test = _train_test_dataset()
    model = EvoPriorAdditiveModel(tree=_tree(), gene_prior=_prior(), alpha_shrinkage=1.0).fit(train)

    components = model.predict_components(test)
    predicted = model.predict_delta(test)

    assert predicted.shape == test.observed_delta.shape
    assert np.isfinite(predicted.to_numpy()).all()
    summed = (
        components["global_component"]
        + components["perturbation_component"]
        + components["lineage_component"]
        + components["gene_prior_component"]
    )
    np.testing.assert_allclose(summed.to_numpy(), components["final_delta"].to_numpy())


def test_evoprior_additive_missing_gene_prior_and_missing_lineage_are_finite():
    train, test = _train_test_dataset()
    test.metadata.loc[:, "cell_type"] = "unknown"
    model = EvoPriorAdditiveModel(tree=_tree(), gene_prior=None, use_gene_prior=True).fit(train)

    predicted = model.predict_delta(test)

    assert np.isfinite(predicted.to_numpy()).all()


def test_evoprior_additive_shuffled_prior_changes_gene_component_only():
    train, test = _train_test_dataset()
    prior = _prior()
    shuffled = prior.shuffled_control(seed=7)
    model = EvoPriorAdditiveModel(tree=_tree(), gene_prior=prior, alpha_shrinkage=10.0).fit(train)
    shuffled_model = EvoPriorAdditiveModel(
        tree=_tree(),
        gene_prior=shuffled,
        alpha_shrinkage=10.0,
    ).fit(train)

    components = model.predict_components(test)
    shuffled_components = shuffled_model.predict_components(test)

    np.testing.assert_allclose(
        components["global_component"].to_numpy(),
        shuffled_components["global_component"].to_numpy(),
    )
    np.testing.assert_allclose(
        components["lineage_component"].to_numpy(),
        shuffled_components["lineage_component"].to_numpy(),
    )
    assert not np.allclose(
        components["gene_prior_component"].to_numpy(),
        shuffled_components["gene_prior_component"].to_numpy(),
    )


def test_evoprior_additive_controlled_synthetic_improves_over_no_lineage_no_prior():
    train, test = _train_test_dataset()
    integrated = EvoPriorAdditiveModel(
        tree=_tree(),
        gene_prior=_prior(),
        alpha_shrinkage=1.0,
    ).fit(train)
    weak = EvoPriorAdditiveModel(
        tree=_tree(),
        gene_prior=None,
        use_lineage_prior=False,
        use_gene_prior=False,
    ).fit(train)

    integrated_pred = integrated.predict_delta(test)
    weak_pred = weak.predict_delta(test)

    assert mean_absolute_error(
        test.observed_delta.to_numpy(),
        integrated_pred.to_numpy(),
    ) < mean_absolute_error(test.observed_delta.to_numpy(), weak_pred.to_numpy())


def _train_test_dataset() -> tuple[DeltaDataset, DeltaDataset]:
    metadata = pd.DataFrame(
        {
            "cell_type": ["myeloid_a", "myeloid_a", "lymphoid_a", "lymphoid_a", "myeloid_b"],
            "perturbation": ["stim", "stim", "stim", "stim", "stim"],
        },
        index=["g1", "g2", "g3", "g4", "g5"],
    )
    control = pd.DataFrame(0.0, index=metadata.index, columns=["A", "B", "C"])
    observed_delta = pd.DataFrame(
        [
            [2.0, 1.0, 0.0],
            [2.2, 1.2, 0.0],
            [-1.0, 0.0, 0.0],
            [-1.1, 0.1, 0.0],
            [2.1, 1.1, 0.0],
        ],
        index=metadata.index,
        columns=["A", "B", "C"],
    )
    dataset = DeltaDataset(
        group_ids=tuple(metadata.index),
        metadata=metadata,
        control_expression=control,
        observed_post_expression=control + observed_delta,
        observed_delta=observed_delta,
    )
    train_index = ["g1", "g2", "g3", "g4"]
    test_index = ["g5"]
    return _subset(dataset, train_index), _subset(dataset, test_index)


def _subset(dataset: DeltaDataset, index: list[str]) -> DeltaDataset:
    return DeltaDataset(
        group_ids=tuple(index),
        metadata=dataset.metadata.loc[index].copy(),
        control_expression=dataset.control_expression.loc[index].copy(),
        observed_post_expression=dataset.observed_post_expression.loc[index].copy(),
        observed_delta=dataset.observed_delta.loc[index].copy(),
    )


def _tree() -> LineageTree:
    return LineageTree.from_edges(
        [
            (None, "root"),
            ("root", "myeloid"),
            ("myeloid", "myeloid_a"),
            ("myeloid", "myeloid_b"),
            ("root", "lymphoid"),
            ("lymphoid", "lymphoid_a"),
        ]
    )


def _prior() -> GenePriorTable:
    return GenePriorTable.from_dataframe(
        pd.DataFrame(
            {
                "gene_symbol": ["A", "B", "C"],
                "conservation_score": [1.0, 0.0, 0.5],
                "ortholog_count": [20, 2, 5],
                "source": ["toy", "toy", "toy"],
                "source_version": ["v1", "v1", "v1"],
            }
        )
    )
