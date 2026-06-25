from evoprior_aivc.data.gears_norman_adapter import (
    parse_perturbation_label,
    perturbation_genes_from_encoded,
)


def test_parse_control_label():
    parsed = parse_perturbation_label("ctrl", control_labels={"ctrl", "control"})

    assert parsed["perturbation"] == "control"
    assert parsed["perturbation_type"] == "control"
    assert parsed["perturbation_genes"] == ""


def test_parse_combo_label_with_plus():
    parsed = parse_perturbation_label("AHR+KLF1", control_labels={"ctrl"})

    assert parsed["perturbation"] == "AHR+KLF1"
    assert parsed["perturbation_type"] == "combo"
    assert perturbation_genes_from_encoded(parsed["perturbation_genes"]) == ("AHR", "KLF1")


def test_parse_single_with_control_partner():
    parsed = parse_perturbation_label("FOSB+ctrl", control_labels={"ctrl"})

    assert parsed["perturbation"] == "FOSB"
    assert parsed["perturbation_type"] == "single"
    assert parsed["perturbation_genes"] == "FOSB"
