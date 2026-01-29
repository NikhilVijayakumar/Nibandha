from typing import Dict, Any, List, Optional, Union
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
        
    def _build_module_breakdown(self, pytest_data: Dict[str, Any], coverage_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Aggregates coverage data by module."""
        files = coverage_data.get("files", {})
        module_stats = self._aggregate_file_stats(files)
        return self._format_module_stats(module_stats)

    def _aggregate_file_stats(self, files: Dict[str, Any]) -> Dict[str, Dict[str, int]]:
        stats: Dict[str, Dict[str, int]] = {}
        for file_path, f_stats in files.items():
            mod_name = self._extract_module_from_path(file_path)
            if not mod_name: continue
            
            if mod_name not in stats:
                stats[mod_name] = {"stmts": 0, "covered": 0, "missed": 0}
            
            s = f_stats.get("summary", {})
            stats[mod_name]["stmts"] += s.get("num_statements", 0)
            stats[mod_name]["covered"] += s.get("covered_lines", 0)
            stats[mod_name]["missed"] += s.get("missing_lines", 0)
        return stats

    def _extract_module_from_path(self, file_path: str) -> Optional[str]:
        # Normalize path
        # Expected pattern: .../src/nikhil/nibandha/MODULENAME/file.py
        parts = file_path.split("src/nikhil/nibandha/")
        if len(parts) < 2:
            # Try relative path or verification environment paths
            if "src/nikhil/nibandha" in file_path:
               parts = file_path.split("src/nikhil/nibandha/")
            else: 
               return None

        subpath = parts[1]
        module_name = subpath.split("/")[0]
        
        # Skip root files like __init__.py if they are not in a submodule
        if ".py" in module_name:
            module_name = "root"
        return module_name

    def _format_module_stats(self, module_stats: Dict[str, Dict[str, int]]) -> List[Dict[str, Any]]:
        breakdown = []
        for name, data in module_stats.items():
            total = data["stmts"]
            covered = data["covered"]
            percent = (covered / total * 100) if total > 0 else 0.0
            
            # Determine grade
            if percent >= 80: grade = "A"
            elif percent >= 70: grade = "B"
            elif percent >= 50: grade = "C"
            elif percent >= 30: grade = "D"
            else: grade = "F"

            breakdown.append({
                "name": name.capitalize(),
                "coverage": round(percent, 1),
                "stmts": total,
                "miss": data["missed"],
                "grade": grade,
                "status": "PASS" if percent >= 80 else "FAIL" # Simplified status rule
            })
            
        return sorted(breakdown, key=lambda x: x["name"])

    def _build_outcomes_by_module(self, pytest_data: Dict[str, Any]) -> Dict[str, Dict[str, int]]:
        # We can simulate this from pytest 'tests' list
        outcomes: Dict[str, Dict[str, int]] = {}
        for test in pytest_data.get("tests", []):
            # nodeid example: tests/unit/reporting/test_foo.py::test_bar
            nodeid = test.get("nodeid", "")
            path_parts = nodeid.split("::")[0].split("/")
            # Attempt to guess module: tests/unit/reporting -> reporting
            if len(path_parts) > 2 and path_parts[1] == "unit":
                 module = path_parts[2]
                 # Remap known modules that don't have their own top-level source package
                 if module == "rotation":
                     module = "logging"
            else:
                 module = "other"
            
            if module not in outcomes:
                outcomes[module] = {"pass": 0, "fail": 0, "error": 0}
            
            outcome = test.get("outcome", "nop")
            if outcome == "passed": outcomes[module]["pass"] += 1
            elif outcome == "failed": outcomes[module]["fail"] += 1
            elif outcome == "error": outcomes[module]["error"] += 1
            
        return outcomes

    def _extract_failures(self, pytest_data: Dict[str, Any]) -> List[Dict[str, str]]:
        failures = []
        for test in pytest_data.get("tests", []):
            if test.get("outcome") in ["failed", "error"]:
                failures.append({
                    "test_name": test.get("nodeid", "Unknown"),
                    "error": test.get("call", {}).get("crash", {}).get("message", "Unknown error"),
                    "traceback": test.get("call", {}).get("longrepr", "")
                })
        return failures

    def _extract_durations(self, pytest_data: Dict[str, Any]) -> List[float]:
        durations = []
        for t in pytest_data.get("tests", []):
            if "duration" in t:
                durations.append(t["duration"])
            else:
                # Fallback to call/setup duration
                d = t.get("call", {}).get("duration", 0) or t.get("setup", {}).get("duration", 0)
                if d > 0:
                    durations.append(d)
        return durations


class E2EDataBuilder:
    """Builds E2E report data."""
    def build(self, results: Dict[str, Any], timestamp: str) -> Dict[str, Any]:
        logger.debug("Building E2E Test Data")
        scenarios = results.get("tests", []) # pytest-json-report key is 'tests'
        total = len(scenarios)
        passed = sum(1 for s in scenarios if s.get("outcome") == "passed")
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
    def build_type_safety(self, errors: List[Dict[str, Any]], timestamp: str) -> Dict[str, Any]:
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
    def build(
        self, 
        unit_data: Dict[str, Any], 
        e2e_data: Dict[str, Any], 
        quality_data: Dict[str, Any], 
        documentation_data: Optional[Dict[str, Any]] = None, 
        dependency_data: Optional[Dict[str, Any]] = None, 
        package_data: Optional[Dict[str, Any]] = None, 
        project_name: str = "Nibandha"
    ) -> Dict[str, Any]:
        """Build data dictionary for unified overview report."""
        logger.info("Building Summary Data for Overview")
        
        # 1. Aggregate Core Metrics
        metrics = self._aggregate_metrics(unit_data, e2e_data, quality_data)
        
        # 2. Generate Action Items and Status
        actions, overall_status = self._generate_actions_and_status(metrics)

        # 3. Calculate Unified Grade
        unified_grade = self._calculate_unified_grade(metrics)

        # 4. Construct Base Result
        result = self._construct_base_result(metrics, actions, overall_status, unified_grade)

        # 5. Enrich with Optional Data
        self._enrich_documentation(result, documentation_data)
        self._enrich_dependencies(result, dependency_data)
        self._enrich_package(result, package_data)
        
        return result

    def _aggregate_metrics(self, u_data: Dict[str, Any], e_data: Dict[str, Any], q_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "unit": {
                "status": u_data.get("status", "UNKNOWN"),
                "total": u_data.get("total", 0),
                "passed": u_data.get("passed", 0),
                "failed": u_data.get("failed", 0) - u_data.get("skipped", 0),
                "rate": u_data.get("pass_rate", 0),
                "grade": u_data.get("grade", "F"),
                "cov_total": u_data.get("coverage_total", 0)
            },
            "e2e": {
                "status": e_data.get("status", "UNKNOWN"),
                "total": e_data.get("total", 0),
                "passed": e_data.get("status_counts", {}).get("pass", 0),
                "failed": e_data.get("status_counts", {}).get("fail", 0),
                "rate": e_data.get("pass_rate", 0),
                "grade": e_data.get("grade", "F")
            },
            "quality": {
                "arch": q_data.get("architecture", {}),
                "type": q_data.get("type_safety", {}),
                "cplx": q_data.get("complexity", {})
            }
        }

    def _generate_actions_and_status(self, metrics: Dict[str, Any]) -> tuple[List[str], str]:
        u = metrics["unit"]
        e = metrics["e2e"]
        q = metrics["quality"]
        
        actions = []
        if u["status"] != "PASS": actions.append(f"- Fix {u['failed']} failing unit tests")
        if e["status"] != "PASS": actions.append(f"- Fix {e['failed']} failing E2E scenarios")
        if u["cov_total"] < 80: actions.append(f"- Improve code coverage (currently {u['cov_total']}%)")
        
        if q["type"].get("status") != "PASS": 
            actions.append(f"- Resolve {q['type'].get('violation_count', 0)} type safety errors")
        if q["cplx"].get("status") != "PASS": 
            actions.append(f"- Refactor {q['cplx'].get('violation_count', 0)} complex functions")
        if q["arch"].get("status") != "PASS": 
            actions.append("- Fix architecture violations")
            
        overall = "🟢 HEALTHY"
        if actions: overall = "🟡 NEEDS ATTENTION"
        
        is_crit = lambda s: "FAIL" in str(s)
        if is_crit(u["status"]) or is_crit(e["status"]) or is_crit(q["arch"].get("status")):
             overall = "🔴 CRITICAL"
             
        return actions, overall

    def _calculate_unified_grade(self, metrics: Dict[str, Any]) -> str:
        grades = [
            str(metrics["unit"]["grade"]),
            str(metrics["e2e"]["grade"]),
            str(metrics["quality"]["arch"].get("grade", "F")),
            str(metrics["quality"]["type"].get("grade", "F")),
            str(metrics["quality"]["cplx"].get("grade", "F"))
        ]
        return Grader.calculate_overall_grade(grades)  # type: ignore

    def _construct_base_result(self, metrics: Dict[str, Any], actions: List[str], overall: str, grade: str) -> Dict[str, Any]:
        u = metrics["unit"]
        e = metrics["e2e"]
        q = metrics["quality"]
        cov_status = "GOOD" if u["cov_total"] > 80 else "NEEDS IMPROVEMENT"
        
        return {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "overall_status": overall,
            "display_grade": grade,
            "grade_color": Grader.get_grade_color(grade),  # type: ignore
            
            "unit_status": "🟢 PASS" if u["status"] == "PASS" else "🔴 FAIL",
            "unit_passed": u["passed"], "unit_failed": u["failed"], 
            "unit_total": u["total"], "unit_pass_rate": u["rate"],
            
            "e2e_status": "🟢 PASS" if e["status"] == "PASS" else "🔴 FAIL",
            "e2e_passed": e["passed"], "e2e_failed": e["failed"],
            "e2e_total": e["total"], "e2e_pass_rate": e["rate"],
            
            "coverage_status": f"🟢 {cov_status}" if cov_status == "GOOD" else f"🟡 {cov_status}",
            "coverage_total": u["cov_total"],
            
            "type_status": "🟢 PASS" if q["type"].get("status") == "PASS" else "🔴 FAIL",
            "type_violations": q["type"].get("violation_count", 0),
            
            "complexity_status": "🟢 PASS" if q["cplx"].get("status") == "PASS" else "🔴 FAIL",
            "complexity_violations": q["cplx"].get("violation_count", 0),
            
            "arch_status": "🟢 PASS" if q["arch"].get("status") == "PASS" else "🔴 FAIL",
            "arch_message": "Clean" if q["arch"].get("status") == "PASS" else "Violations Detected",
            
            "action_items": "\n".join(actions) if actions else "- No urgent actions required."
        }

    def _enrich_documentation(self, result: Dict[str, Any], doc_data: Optional[Dict[str, Any]]) -> None:
        if not doc_data:
            result.update({"doc_coverage": "N/A", "doc_status": "⚪ Not Run",
                           "func_doc_pct": "N/A", "tech_doc_pct": "N/A", "test_doc_pct": "N/A"})
            return

        func = self._calc_doc_pct(doc_data.get("functional", {}))
        tech = self._calc_doc_pct(doc_data.get("technical", {}))
        test = self._calc_doc_pct(doc_data.get("test", {}))
        
        avg = (func + tech + test) / 3
        result["doc_coverage"] = f"{avg:.1f}"
        result["doc_status"] = "🟢 GOOD" if avg > 80 else "🟡 NEEDS IMPROVEMENT"
        result["func_doc_pct"] = f"{func:.1f}"
        result["tech_doc_pct"] = f"{tech:.1f}"
        result["test_doc_pct"] = f"{test:.1f}"

    def _calc_doc_pct(self, section_data: Dict[str, Any]) -> float:
        stats = section_data.get("stats", {})
        total = stats.get("documented", 0) + stats.get("missing", 0)
        return (stats.get("documented", 0) / total * 100) if total > 0 else 0.0

    def _enrich_dependencies(self, result: Dict[str, Any], dep_data: Optional[Dict[str, Any]]) -> None:
        if dep_data:
            result.update({
                "dep_status": dep_data.get("status", "⚪ Not Run"),
                "dep_total_modules": dep_data.get("total_modules", 0),
                "dep_total_deps": dep_data.get("total_dependencies", 0),
                "dep_circular": dep_data.get("circular_count", 0)
            })
        else:
             result.update({"dep_status": "⚪ Not Run", "dep_total_modules": "N/A", 
                            "dep_total_deps": "N/A", "dep_circular": "N/A"})

    def _enrich_package(self, result: Dict[str, Any], pkg_data: Optional[Dict[str, Any]]) -> None:
        if pkg_data:
            result.update({
                "pkg_status": pkg_data.get("status", "⚪ Not Run"),
                "pkg_total": pkg_data.get("total_packages", 0),
                "pkg_outdated": pkg_data.get("outdated_count", 0),
                "pkg_health_score": pkg_data.get("health_score", 0)
            })
        else:
             result.update({"pkg_status": "⚪ Not Run", "pkg_total": "N/A", 
                            "pkg_outdated": "N/A", "pkg_health_score": "N/A"})
