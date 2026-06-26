import numpy as np
import pandas as pd

from evoprior_aivc.baselines import ControlMeanBaseline, MeanDeltaBaseline
from evoprior_aivc.baselines.base import DeltaDataset
from evoprior_aivc.baselines.gene_prior_correction import GenePriorCorrectionBaseline
from evoprior_aivc.evaluation.metrics import mean_absolute_error
from evoprior_aivc.priors.gene_prior_table import GenePriorTable


def test_gene_prior_correction_improves_controlled_residual_case():
    dataset = _controlled_dataset()
    prior = GenePriorTable.from_dataframe(
        pd.DataFrame(
            {
                "gene_symbol": ["A", "B", "C"],
                "conservation_score": [1.0, 0.0, 0.0],
                "source": ["toy", "toy", "toy"],
                "source_version": ["v1", "v1", "v1"],
            }
        )
    )
    base = ControlMeanBaseline().fit(dataset)
    base_pred = base.predict_delta(dataset)
    correction = GenePriorCorrectionBaseline(
        base_baseline=ControlMeanBaseline(),
        gene_prior=prior,
        alpha=0.0,
    ).fit(dataset)

    corrected = correction.predict_delta(dataset)

    assert mean_absolute_error(
        dataset.observed_delta.to_numpy(),
        corrected.to_numpy(),
    ) < mean_absolute_error(dataset.observed_delta.to_numpy(), base_pred.to_numpy())


def test_gene_prior_correction_missing_prior_and_shuffled_are_finite():
    dataset = _controlled_dataset()
    prior = GenePriorTable.from_dataframe(
        pd.DataFrame(
            {
                "gene_symbol": ["A", "B"],
                "conservation_score": [1.0, 0.0],
            }
        )
    )
    shuffled = prior.shuffled_control(seed=1)

    for table in (prior, shuffled):
        baseline = GenePriorCorrectionBaseline(
            base_baseline=MeanDeltaBaseline(fallback="global"),
            gene_prior=table,
        ).fit(dataset)
        predicted = baseline.predict_delta(dataset)
        assert predicted.shape == dataset.observed_delta.shape
        assert np.isfinite(predicted.to_numpy()).all()


def test_gene_prior_correction_no_correction_mode_matches_base():
    dataset = _controlled_dataset()
    prior = GenePriorTable.from_dataframe(
        pd.DataFrame({"gene_symbol": ["A", "B", "C"], "conservation_score": [1, 0, 0]})
    )
    base = MeanDeltaBaseline(fallback="global").fit(dataset)
    wrapped = GenePriorCorrectionBaseline(
        base_baseline=MeanDeltaBaseline(fallback="global"),
        gene_prior=prior,
        mode="no_correction",
    ).fit(dataset)

    assert np.allclose(base.predict_delta(dataset), wrapped.predict_delta(dataset))


def _controlled_dataset() -> DeltaDataset:
    metadata = pd.DataFrame(
        {
            "cell_type": ["t", "t", "b", "b"],
            "perturbation": ["stim", "stim", "stim", "stim"],
        },
        index=["g1", "g2", "g3", "g4"],
    )
    control = pd.DataFrame(np.zeros((4, 3)), index=metadata.index, columns=["A", "B", "C"])
    observed_delta = pd.DataFrame(
        [[2.0, 0.0, 0.0], [2.0, 0.1, 0.0], [0.2, 0.0, 0.0], [0.2, 0.1, 0.0]],
        index=metadata.index,
        columns=["A", "B", "C"],
    )
    return DeltaDataset(
        group_ids=tuple(metadata.index),
        metadata=metadata,
        control_expression=control,
        observed_post_expression=control + observed_delta,
        observed_delta=observed_delta,
    )
