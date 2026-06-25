import pandas as pd

from evoprior_aivc.data.perturbation_features import PerturbationFeatureEncoder


def test_perturbation_feature_encoder_uses_train_vocab_and_marks_unknown_genes():
    train_metadata = pd.DataFrame(
        {
            "perturbation_genes": ["A", "B", "A;B"],
            "perturbation_type": ["single", "single", "combo"],
            "cell_type": ["K562", "K562", "K562"],
        },
        index=["A", "B", "A+B"],
    )
    query_metadata = pd.DataFrame(
        {
            "perturbation_genes": ["A;C"],
            "perturbation_type": ["combo"],
            "cell_type": ["K562"],
        },
        index=["A+C"],
    )

    encoder = PerturbationFeatureEncoder().fit(train_metadata)
    features = encoder.transform(query_metadata)

    assert "gene::A" in features.columns
    assert "gene::C" not in features.columns
    assert features.loc["A+C", "gene::A"] == 1.0
    assert features.loc["A+C", "unknown_gene_count"] == 1.0
    assert features.loc["A+C", "known_gene_fraction"] == 0.5
    assert features.loc["A+C", "is_combo"] == 1.0
