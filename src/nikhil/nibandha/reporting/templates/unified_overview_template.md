# Pravaha Test & Quality Report

**Generated:** {date}  
**Overall Status:** {overall_status}  
**Project Grade:** <span style="color:{grade_color}; font-size: 2.5em; font-weight: bold;">{display_grade}</span>

---

## 📊 Quick Summary

| Category | Status | Key Metrics |
| :--- | :---: | :--- |
| **Unit Tests** | {unit_status} | {unit_passed}/{unit_total} passed ({unit_pass_rate}%) |
| **E2E Tests** | {e2e_status} | {e2e_passed}/{e2e_total} passed ({e2e_pass_rate}%) |
| **Code Coverage** | {coverage_status} | {coverage_total}% |
| **Type Safety** | {type_status} | {type_violations} errors |
| **Complexity** | {complexity_status} | {complexity_violations} violations |
| **Architecture** | {arch_status} | {arch_message} |

---

## 🧪 Test Reports

### Unit Tests
- **Total**: {unit_total} tests
- **Passed**: {unit_passed} ✅
- **Failed**: {unit_failed} ❌
- **Coverage**: {coverage_total}%

![Unit Outcomes](assets/images/unit_outcomes.png)

ðŸ“„ [Detailed Unit Test Report](details/unit_report.md)

---

### E2E Tests
- **Total**: {e2e_total} scenarios
- **Passed**: {e2e_passed} ✅
- **Failed**: {e2e_failed} ❌

![E2E Status](assets/images/e2e_status.png)

ðŸ“„ [Detailed E2E Report](details/e2e_report.md)

---

## 🔍 Code Quality Reports

### Type Safety (mypy)
- **Status**: {type_status}
- **Total Errors**: {type_violations}

![Type Errors](assets/images/quality/type_errors_by_module.png)

ðŸ“„ [Detailed Type Safety Report](details/type_safety_report.md)

---

### Complexity (ruff)
- **Status**: {complexity_status}
- **Violations**: {complexity_violations}

![Complexity](assets/images/quality/complexity_distribution.png)

ðŸ“„ [Detailed Complexity Report](details/complexity_report.md)

---

### Architecture (import-linter)
- **Status**: {arch_status}

![Architecture](assets/images/quality/architecture_status.png)

ðŸ“„ [Detailed Architecture Report](details/architecture_report.md)

---

## 🎯 Action Items

{action_items}

---

## 📂 Report Structure

```
Report/
  summary.md           â† You are here
  assets/              â† All visualizations and data files
  details/             â† Detailed reports
```
