from pathlib import Path

import pandas as pd

from evoprior_aivc.evaluation.component_audit import (
    component_correlation_summary,
    component_magnitude_summary,
    top_component_genes,
    write_component_audit_report,
)


def test_component_audit_summarizes_magnitudes_and_top_genes(tmp_path: Path):
    components = {
        "global_component": pd.DataFrame([[1.0, 0.0]], columns=["A", "B"]),
        "lineage_component": pd.DataFrame([[0.0, 2.0]], columns=["A", "B"]),
        "gene_prior_component": pd.DataFrame([[3.0, 0.0]], columns=["A", "B"]),
        "final_delta": pd.DataFrame([[4.0, 2.0]], columns=["A", "B"]),
    }

    magnitudes = component_magnitude_summary(components)
    correlations = component_correlation_summary(components)
    top = top_component_genes(components["gene_prior_component"], n=1)
    summary = write_component_audit_report(
        tmp_path / "component_audit.md",
        title="Audit",
        components=components,
        claim_boundary="test only",
    )

    assert set(magnitudes["component"]) == {
        "global_component",
        "lineage_component",
        "gene_prior_component",
    }
    assert correlations.shape[0] == 3
    assert top["gene"].tolist() == ["A"]
    assert summary["gene_prior_collapsed"] is False
    assert (tmp_path / "component_audit.md").exists()
