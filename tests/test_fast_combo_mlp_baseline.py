import numpy as np
import pandas as pd

from evoprior_aivc.baselines import DeltaDataset, FastComboMLPConfig, FastComboMLPPCA


def test_fast_combo_mlp_pca_fits_and_predicts_finite_delta():
    train = _toy_dataset()
    query = DeltaDataset(
        group_ids=("A+B", "A+C"),
        metadata=pd.DataFrame(
            {
                "perturbation": ["A+B", "A+C"],
                "perturbation_type": ["combo", "combo"],
                "perturbation_genes": ["A;B", "A;C"],
                "cell_type": ["K562", "K562"],
            },
            index=["A+B", "A+C"],
        ),
        control_expression=pd.DataFrame(
            [[0.0, 0.0], [0.0, 0.0]],
            index=["A+B", "A+C"],
            columns=["g1", "g2"],
        ),
        observed_post_expression=pd.DataFrame(
            [[1.5, 1.0], [0.5, 0.5]],
            index=["A+B", "A+C"],
            columns=["g1", "g2"],
        ),
        observed_delta=pd.DataFrame(
            [[1.5, 1.0], [0.5, 0.5]],
            index=["A+B", "A+C"],
            columns=["g1", "g2"],
        ),
    )
    model = FastComboMLPPCA(
        FastComboMLPConfig(
            pca_components=2,
            hidden_layer_sizes=(8,),
            max_iter=200,
            early_stopping=False,
            random_state=15,
        )
    ).fit(train)

    predicted = model.predict_delta(query)
    manifest = model.manifest()

    assert predicted.shape == (2, 2)
    assert list(predicted.columns) == ["g1", "g2"]
    assert np.isfinite(predicted.to_numpy()).all()
    assert manifest["fit_status"]["backend"] == "sklearn"
    assert manifest["feature_manifest"]["n_gene_features"] == 3
    assert not model.training_curve().empty


def _toy_dataset() -> DeltaDataset:
    metadata = pd.DataFrame(
        {
            "perturbation": ["A", "B", "C", "A+B", "A+C"],
            "perturbation_type": ["single", "single", "single", "combo", "combo"],
            "perturbation_genes": ["A", "B", "C", "A;B", "A;C"],
            "cell_type": ["K562", "K562", "K562", "K562", "K562"],
        },
        index=["A", "B", "C", "A+B", "A+C"],
    )
    delta = pd.DataFrame(
        [
            [1.0, 0.0],
            [0.0, 1.0],
            [0.5, 0.5],
            [1.5, 1.0],
            [1.0, 0.5],
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
