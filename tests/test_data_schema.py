import numpy as np
import pytest

from evoprior_aivc.data.synthetic import make_synthetic_perturbation_adata
from evoprior_aivc.data.validate import (
    infer_control_mask,
    normalize_metadata_labels,
    validate_adata_schema,
)


def test_synthetic_adata_satisfies_canonical_schema():
    adata = make_synthetic_perturbation_adata(seed=1)

    report = validate_adata_schema(adata)

    assert report.n_obs == 3 * 4 * 2 * 6
    assert report.n_vars == 20
    assert report.preferred_obs_missing == ()
    assert {"cell_type", "perturbation", "is_control", "donor", "batch"}.issubset(
        report.obs_fields
    )
    assert {"gene_id", "gene_symbol"}.issubset(report.var_fields)


def test_metadata_normalization_and_control_inference_are_consistent():
    adata = make_synthetic_perturbation_adata(seed=2)
    adata.obs.loc[adata.obs.index[0], "perturbation"] = " Non Targeting "
    adata.obs.loc[adata.obs.index[0], "cell_type"] = " CD4 T "
    adata.obs = adata.obs.drop(columns=["is_control"])

    normalize_metadata_labels(adata)
    control_mask = infer_control_mask(adata)

    assert adata.obs.iloc[0]["perturbation"] == "non_targeting"
    assert adata.obs.iloc[0]["cell_type"] == "cd4_t"
    assert bool(control_mask.iloc[0])
    assert "is_control" in adata.obs.columns


def test_schema_validation_rejects_missing_required_obs_field():
    adata = make_synthetic_perturbation_adata(seed=3)
    adata.obs = adata.obs.drop(columns=["cell_type"])

    with pytest.raises(ValueError, match="cell_type"):
        validate_adata_schema(adata)


def test_schema_validation_rejects_missing_gene_identifier():
    adata = make_synthetic_perturbation_adata(seed=4)
    adata.var = adata.var.drop(columns=["gene_id", "gene_symbol"])

    with pytest.raises(ValueError, match="gene identifier"):
        validate_adata_schema(adata)


def test_synthetic_data_contains_known_delta_pattern():
    adata = make_synthetic_perturbation_adata(seed=0, cells_per_group=8)
    control = np.asarray(adata[adata.obs["perturbation"] == "control"].X).mean(axis=0)
    pert_a = np.asarray(adata[adata.obs["perturbation"] == "pert_a"].X).mean(axis=0)
    delta = pert_a - control

    assert delta[0] > 2.0
    assert delta[3] == pytest.approx(2.0, abs=0.15)
