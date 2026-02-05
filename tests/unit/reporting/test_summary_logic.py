
import pytest
from nibandha.reporting.shared.data.data_builders import SummaryDataBuilder

class TestSummaryDataBuilder:
    
    def test_build_integration(self):
        """RPT-SUM-001: Verify aggregation of all reports."""
        builder = SummaryDataBuilder()
        
        unit = {"status": "PASS", "grade": "A", "pass_rate": 100, "coverage_total": 95}
        e2e = {"status": "PASS", "grade": "A"}
        quality = {
            "architecture": {"status": "PASS", "grade": "A"}, 
            "type_safety": {"status": "PASS", "grade": "A"}, 
            "complexity": {"status": "PASS", "grade": "A"},
            "hygiene": {"status": "PASS", "grade": "A", "violation_count": 0},
            "security": {"status": "PASS", "grade": "A", "violation_count": 0},
            "duplication": {"status": "PASS", "grade": "A", "violation_count": 0}
        }
        doc = {"functional": {}, "technical": {}, "test": {}} # simplified
        
        res = builder.build(unit, e2e, quality, documentation_data=doc)
        
        assert res["overall_status"] == "🟢 HEALTHY"
        assert res["display_grade"] == "A"
        assert "No urgent actions required" in res["action_items"]
        
    def test_build_critical_path(self):
        """RPT-SUM-002: Verify Critical status triggers."""
        builder = SummaryDataBuilder()
        
        unit = {"status": "FAIL", "grade": "F", "failed": 5, "coverage_total": 50} # Critical failure
        e2e = {"status": "PASS"} # ...
        quality = {"architecture": {"status": "PASS"}, "type_safety": {}, "complexity": {}}
        
        res = builder.build(unit, e2e, quality)
        
        assert "CRITICAL" in res["overall_status"]
        assert "Fix 5 failing unit tests" in res["action_items"]
        
    def test_grade_averaging(self):
        """RPT-SUM-003: Verify grade averaging logic."""
        builder = SummaryDataBuilder()
        
        # Mix of grades
        unit = {"grade": "A"}
        e2e = {"grade": "C"}
        quality = {"architecture": {"grade": "F"}, "type_safety": {"grade": "B"}, "complexity": {"grade": "A"}}
        
        res = builder.build(unit, e2e, quality)
        
        # Grader logic returns F if any component is F (Critical Failure)
        assert res["display_grade"] == "F"
