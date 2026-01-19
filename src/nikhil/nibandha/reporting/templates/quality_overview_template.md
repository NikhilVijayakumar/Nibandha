# Code Quality Overview

**Date:** {date}  
**Overall Status:** {overall_status}  
**Grade:** <span style="color:{grade_color}; font-size: 2em; font-weight: bold;">{display_grade}</span>

---

## 🏗️ Architecture & Design

| Check | Tool | Status | Violations |
| :--- | :--- | :---: | :---: |
| **Clean Architecture** | `import-linter` | {arch_status} | {arch_violations} |
| **Folder Structure** | - | {struct_status} | {struct_violations} |

---

## 🛡️ Code Safety & Complexity

| Check | Tool | Status | Violations |
| :--- | :--- | :---: | :---: |
| **Type Safety** | `mypy --strict` | {type_status} | {type_violations} |
| **Complexity (SRP)** | `ruff (C901)` | {cplx_status} | {cplx_violations} |

---

## 📝 Key Recommendations

1. Address type errors starting with modules that have the highest count
2. Refactor complex functions to improve maintainability
3. Review and fix any architecture violations to maintain clean separation

---

## 🔗 Detailed Reports

- [Architecture Report](./architecture_report.md)
- [Type Safety Report](./type_safety_report.md)
- [Complexity Report](./complexity_report.md)
