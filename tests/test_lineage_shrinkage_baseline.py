import numpy as np

from evoprior_aivc.baselines import MeanDeltaBaseline
from evoprior_aivc.baselines.base import DeltaDataset, build_delta_dataset
from evoprior_aivc.baselines.lineage_shrinkage import LineageShrinkageBaseline
from evoprior_aivc.data.pseudobulk import aggregate_pseudobulk
from evoprior_aivc.data.synthetic_lineage import (
    heldout_cell_type_split,
    make_synthetic_lineage_adata,
    make_synthetic_lineage_tree,
)
from evoprior_aivc.evaluation.metrics import mean_absolute_error


def test_lineage_shrinkage_heldout_sibling_beats_unrelated_control_case():
    dataset = _lineage_delta_dataset()
    split = heldout_cell_type_split(dataset.metadata, heldout_cell_type="myeloid_b")
    train = _subset(dataset, split == "train")
    test = _subset(dataset, split == "test")
    tree = make_synthetic_lineage_tree()

    lineage = LineageShrinkageBaseline(tree=tree, tau=1.5, shrinkage=1.0).fit(train)
    mean = MeanDeltaBaseline(fallback="global").fit(train)

    lineage_pred = lineage.predict_delta(test)
    mean_pred = mean.predict_delta(test)

    assert mean_absolute_error(
        test.observed_delta.to_numpy(),
        lineage_pred.to_numpy(),
    ) < mean_absolute_error(
        test.observed_delta.to_numpy(),
        mean_pred.to_numpy(),
    )


def test_lineage_shrinkage_single_cell_type_is_safe_noop():
    dataset = _lineage_delta_dataset()
    mask = dataset.metadata["cell_type"] == "myeloid_a"
    single = _subset(dataset, mask)
    tree = make_synthetic_lineage_tree()

    baseline = LineageShrinkageBaseline(tree=tree, fallback_mode="global").fit(single)
    predictions = baseline.predict_delta(single)

    assert baseline.is_noop_
    assert predictions.shape == single.observed_delta.shape
    assert np.isfinite(predictions.to_numpy()).all()


def test_lineage_shrinkage_unknown_cell_type_fallback_or_error():
    dataset = _lineage_delta_dataset()
    train = _subset(dataset, dataset.metadata["cell_type"] != "myeloid_b")
    query = _subset(dataset, dataset.metadata["cell_type"] == "myeloid_b")
    query.metadata.loc[:, "cell_type"] = "unknown_cell_type"
    tree = make_synthetic_lineage_tree()

    baseline = LineageShrinkageBaseline(tree=tree, fallback_mode="global").fit(train)
    predictions = baseline.predict_delta(query)

    expected = train.observed_delta.groupby(train.metadata["perturbation"]).mean()
    first_perturbation = query.metadata.iloc[0]["perturbation"]
    np.testing.assert_allclose(
        predictions.iloc[0].to_numpy(dtype=float),
        expected.loc[first_perturbation].to_numpy(dtype=float),
    )


def _lineage_delta_dataset():
    adata = make_synthetic_lineage_adata(seed=4, cells_per_group=8)
    expression, metadata = aggregate_pseudobulk(adata)
    return build_delta_dataset(expression, metadata)


def _subset(dataset: DeltaDataset, mask) -> DeltaDataset:
    mask = np.asarray(mask, dtype=bool)
    index = dataset.metadata.index[mask]
    return DeltaDataset(
        group_ids=tuple(index),
        metadata=dataset.metadata.loc[index].copy(),
        control_expression=dataset.control_expression.loc[index].copy(),
        observed_post_expression=dataset.observed_post_expression.loc[index].copy(),
        observed_delta=dataset.observed_delta.loc[index].copy(),
    )
