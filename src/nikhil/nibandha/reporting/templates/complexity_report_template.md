# Logic Complexity Report

**Date:** {date}  
**Tool:** `ruff (C901)`  
**Status:** {overall_status}  
**Grade:** <span style="color:{grade_color}; font-size: 1.5em; font-weight: bold;">{display_grade}</span>

---

## 📊 Summary

| Metric | Value |
| :--- | :---: |
| **Total Violations** | {total_violations} |
| **Max Allowed Complexity** | 10 |
| **Status** | {overall_status} |

---

## 🧠 Complexity Score by Module

{module_table}

---

## 📉 Complexity Distribution

![Complexity Distribution](../assets/images/quality/complexity_distribution.png)

---

## 🐢 Most Complex Functions

<details>
<summary>Click to expand detailed violations</summary>

{top_complex_functions}

</details>

---

## 🛠️ Action Items

- [ ] Refactor high-complexity functions into smaller helpers
- [ ] Apply Strategy pattern to reduce `if/else` chains  
- [ ] Use early returns to reduce nesting depth
