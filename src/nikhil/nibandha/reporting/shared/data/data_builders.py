from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import json
import logging

logger = logging.getLogger("nibandha.reporting")
from ...shared.domain.grading import Grader

class UnitDataBuilder:
    """Builds unit test report data from pytest JSON and coverage data."""
    
    def build(self, pytest_data: Dict[str, Any], coverage_data: Dict[str, Any], timestamp: str) -> Dict[str, Any]:
        logger.debug("Building Unit Test Data")
        summary = pytest_data.get("summary", {})
        total = summary.get("total", 0)
        passed = summary.get("passed", 0)
        failed = summary.get("failed", 0)
        skipped = summary.get("skipped", 0)
        
        pass_rate = (passed / total * 100) if total > 0 else 0.0
        status = "PASS" if failed == 0 and total > 0 else "FAIL"
        
        # Coverage
        cov_totals = coverage_data.get("totals", {})
        cov_percent = cov_totals.get("percent_covered", 0.0)
        
        # Breakdown
        module_breakdown = self._build_module_breakdown(pytest_data, coverage_data)
        outcomes_by_module = self._build_outcomes_by_module(pytest_data)
        coverage_by_module = {m["name"].lower(): m["coverage"] for m in module_breakdown}
        
        return {
            "date": timestamp,
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "pass_rate": round(pass_rate, 1),
            "status": status,
            "coverage_total": round(cov_percent, 1),
            "coverage_by_module": coverage_by_module,
            "outcomes_by_module": outcomes_by_module,
            "module_breakdown": module_breakdown,
            "failures": self._extract_failures(pytest_data),
            "durations": self._extract_durations(pytest_data)
        }
        
    def _build_module_breakdown(self, pytest_data, coverage_data):
        # Placeholder for complex mapping, implemented simply for now
        # In real impl, we'd map file paths to modules
        return []

    def _build_outcomes_by_module(self, pytest_data):
        # We can simulate this from pytest 'tests' list
        outcomes = {}
        for test in pytest_data.get("tests", []):
            # nodeid example: tests/unit/reporting/test_foo.py::test_bar
            path_parts = test.get("nodeid", "").split("::")[0].split("/")
            # Attempt to guess module: tests/unit/reporting -> reporting
            if len(path_parts) > 2 and path_parts[1] == "unit":
                 module = path_parts[2]
            else:
                 module = "other"
            
            if module not in outcomes:
                outcomes[module] = {"pass": 0, "fail": 0, "error": 0}
            
            outcome = test.get("outcome", "nop")
            if outcome == "passed": outcomes[module]["pass"] += 1
            elif outcome == "failed": outcomes[module]["fail"] += 1
            elif outcome == "error": outcomes[module]["error"] += 1
            
        return outcomes

    def _extract_failures(self, pytest_data):
        failures = []
        for test in pytest_data.get("tests", []):
            if test.get("outcome") in ["failed", "error"]:
                failures.append({
                    "test_name": test.get("nodeid"),
                    "error": test.get("call", {}).get("crash", {}).get("message", "Unknown error"),
                    "traceback": test.get("call", {}).get("longrepr", "")
                })
        return failures

    def _extract_durations(self, pytest_data):
        return [t.get("duration", 0) for t in pytest_data.get("tests", []) if "duration" in t]


class E2EDataBuilder:
    """Builds E2E report data."""
    def build(self, results: Dict[str, Any], timestamp: str) -> Dict[str, Any]:
        logger.debug("Building E2E Test Data")
        scenarios = results.get("scenarios", [])
        total = len(scenarios)
        passed = sum(1 for s in scenarios if s.get("status") == "pass")
        failed = total - passed
        
        pass_rate = (passed / total * 100) if total > 0 else 0.0
        
        return {
            "date": timestamp,
            "total_scenarios": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": round(pass_rate, 1),
            "status": "PASS" if failed == 0 and total > 0 else "FAIL",
            "status_counts": {"pass": passed, "fail": failed},
            "scenarios": scenarios
        }

class QualityDataBuilder:
    """Builds quality report data."""
    # Placeholder implementation
    def build_type_safety(self, errors: List[Dict], timestamp: str) -> Dict[str, Any]:
        return {
            "date": timestamp,
            "total_errors": len(errors),
            "status": "PASS" if not errors else "FAIL",
            "errors_by_module": {},
            "errors_by_category": {},
            "detailed_errors": errors
        }

class SummaryDataBuilder:
    """Aggregates all data for summary report."""
    def build(self, unit_data: Dict, e2e_data: Dict, quality_data: Dict, project_name="Nibandha") -> Dict[str, Any]:
        """
        Build data dictionary for unified overview report.
        Expects enriched data from other builders.
        """
        logger.info("Building Summary Data for Overview")
        
        # Unit Checks
        u_status = unit_data.get("status", "UNKNOWN")
        u_total = unit_data.get("total", 0)
        u_passed = unit_data.get("passed", 0)
        u_failed = unit_data.get("failed", 0) - unit_data.get("skipped", 0) # Adjust if needed
        u_rate = unit_data.get("pass_rate", 0)
        
        # E2E Checks
        e_status = e2e_data.get("status", "UNKNOWN")
        e_total = e2e_data.get("total", 0)
        e_passed = e2e_data.get("status_counts", {}).get("pass", 0)
        e_failed = e2e_data.get("status_counts", {}).get("fail", 0)
        e_rate = e2e_data.get("pass_rate", 0)
        
        # Coverage
        cov_total = unit_data.get("coverage_total", 0)
        cov_status = "GOOD" if cov_total > 80 else "NEEDS IMPROVEMENT"
        
        # Quality
        arch = quality_data.get("architecture", {})
        type_ = quality_data.get("type_safety", {})
        cplx = quality_data.get("complexity", {})
        
        arch_status = arch.get("status", "UNKNOWN")
        type_status = type_.get("status", "UNKNOWN")
        cplx_status = cplx.get("status", "UNKNOWN")
        
        # Action Items
        actions = []
        if u_status != "PASS": actions.append(f"- Fix {u_failed} failing unit tests")
        if e_status != "PASS": actions.append(f"- Fix {e_failed} failing E2E scenarios")
        if cov_total < 80: actions.append(f"- Improve code coverage (currently {cov_total}%)")
        if type_status != "PASS": actions.append(f"- Resolve {type_.get('violation_count', 0)} type safety errors")
        if cplx_status != "PASS": actions.append(f"- Refactor {cplx.get('violation_count', 0)} complex functions")
        if arch_status != "PASS": actions.append("- Fix architecture violations")
        
        overall = "🟢 HEALTHY"
        if actions:
             overall = "🟡 NEEDS ATTENTION"
        if "FAIL" in u_status or "FAIL" in e_status or "FAIL" in arch_status:
             overall = "🔴 CRITICAL"

        if "FAIL" in u_status or "FAIL" in e_status or "FAIL" in arch_status:
             overall = "🔴 CRITICAL"

        # Unified Grade
        grade_list = [
            unit_data.get("grade", "F"),
            e2e_data.get("grade", "F"),
            arch.get("grade", "F"),
            type_.get("grade", "F"),
            cplx.get("grade", "F")
        ]
        unified_grade = Grader.calculate_overall_grade(grade_list)

        return {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "overall_status": overall,
            "display_grade": unified_grade,
            "grade_color": Grader.get_grade_color(unified_grade),
            
            # Unit
            "unit_status": "🟢 PASS" if u_status == "PASS" else "🔴 FAIL",
            "unit_passed": u_passed,
            "unit_failed": unit_data.get("failed", 0),
            "unit_total": u_total,
            "unit_pass_rate": u_rate,
            
            # E2E
            "e2e_status": "🟢 PASS" if e_status == "PASS" else "🔴 FAIL",
            "e2e_passed": e_passed,
            "e2e_failed": e_failed,
            "e2e_total": e_total,
            "e2e_pass_rate": e_rate,
            
            # Coverage
            "coverage_status": f"🟢 {cov_status}" if cov_status == "GOOD" else f"🟡 {cov_status}",
            "coverage_total": cov_total,
            
            # Quality
            "type_status": "🟢 PASS" if type_status == "PASS" else "🔴 FAIL",
            "type_violations": type_.get("violation_count", 0),
            
            "complexity_status": "🟢 PASS" if cplx_status == "PASS" else "🔴 FAIL",
            "complexity_violations": cplx.get("violation_count", 0),
            
            "arch_status": "🟢 PASS" if arch_status == "PASS" else "🔴 FAIL",
            "arch_message": "Clean" if arch_status == "PASS" else "Violations Detected",
            
            "action_items": "\n".join(actions) if actions else "- No urgent actions required."
        }
