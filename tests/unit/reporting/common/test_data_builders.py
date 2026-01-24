import pytest
from nibandha.reporting.shared.data.data_builders import UnitDataBuilder, E2EDataBuilder

@pytest.fixture
def unit_builder():
    return UnitDataBuilder()

@pytest.fixture
def e2e_builder():
    return E2EDataBuilder()

def test_unit_builder_metrics(unit_builder):
    pytest_data = {
        "summary": {"total": 10, "passed": 8, "failed": 2, "skipped": 0},
        "tests": [
            {"nodeid": "tests/unit/reporting/test_foo.py::test_1", "outcome": "passed", "duration": 0.1},
            {"nodeid": "tests/unit/reporting/test_foo.py::test_2", "outcome": "failed", "call": {"crash": {"message": "error"}}}
        ]
    }
    cov_data = {"totals": {"percent_covered": 85.5}}
    
    result = unit_builder.build(pytest_data, cov_data, "2026-01-01")
    
    assert result["total_tests"] == 10
    assert result["pass_rate"] == 80.0
    assert result["status"] == "FAIL"
    assert result["coverage_total"] == 85.5
    assert len(result["failures"]) == 1
    assert result["failures"][0]["error"] == "error"
    assert "reporting" in result["outcomes_by_module"]
    assert result["outcomes_by_module"]["reporting"]["fail"] == 1

def test_e2e_builder_metrics(e2e_builder):
    results = {
        "tests": [
            {"nodeid": "s1", "outcome": "passed"},
            {"nodeid": "s2", "outcome": "failed"}
        ]
    }
    
    result = e2e_builder.build(results, "2026-01-01")
    
    assert result["total_scenarios"] == 2
    assert result["passed"] == 1
    assert result["pass_rate"] == 50.0
    assert result["status"] == "FAIL"
    assert result["status_counts"]["pass"] == 1
