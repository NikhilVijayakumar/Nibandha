# Type Safety Report

**Date:** {date}  
**Tool:** `mypy --strict`  
**Status:** {overall_status}  
**Grade:** <span style="color:{grade_color}; font-size: 1.5em; font-weight: bold;">{display_grade}</span>

---

## 📊 Summary

| Metric | Value |
| :--- | :---: |
| **Total Errors** | {total_errors} |
| **Status** | {overall_status} |

---

## 📊 Error Categories

{category_table}

![Error Categories](../assets/images/quality/error_categories.png)

---

## 🛡️ Type Coverage by Module

{module_table}

---

## 📉 Error Distribution

![Type Errors by Module](../assets/images/quality/type_errors_by_module.png)

---

## 🚫 Critical Type Errors

<details>
<summary>Click to expand error details</summary>

{detailed_errors}

</details>

---

## 🛠️ Action Items

- [ ] Add missing type hints to function signatures
- [ ] Resolve `Any` types in strict modules
- [ ] Add return type annotations where missing
