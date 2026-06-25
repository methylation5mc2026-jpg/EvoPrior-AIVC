from scripts.diagnose_official_gears import classify_official_gears_status


def test_classify_official_gears_uses_venv_import_as_run_blocked():
    status = classify_official_gears_status(
        main_probes=[
            {"module": "torch", "importable": False},
            {"module": "gears", "importable": False},
            {"module": "torch_geometric", "importable": False},
        ],
        venv_probe={"gears_import_ok": True},
        wrapper_result={"returncode": 0},
    )

    assert status["status"] == "import_ok_run_blocked"
    assert status["blocker_category"] == "api_mismatch"


def test_classify_official_gears_missing_everywhere_is_dependency_blocked():
    status = classify_official_gears_status(
        main_probes=[
            {"module": "torch", "importable": False},
            {"module": "gears", "importable": False},
            {"module": "torch_geometric", "importable": False},
        ],
        venv_probe={"gears_import_ok": False},
        wrapper_result={"returncode": 1},
    )

    assert status["status"] == "dependency_blocked"
    assert status["blocker_category"] == "import_missing"
