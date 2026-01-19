# Clean Architecture Report

**Date:** {date}  
**Tool:** `import-linter`  
**Tool:** `import-linter`  
**Status:** {overall_status}  
**Grade:** <span style="color:{grade_color}; font-size: 1.5em; font-weight: bold;">{display_grade}</span>

---

## 📊 Summary

![Architecture Status](../assets/images/quality/architecture_status.png)

---

## 🏗️ Layer Dependency Summary

{module_breakdown}

---

## 🚫 Detailed Violations

{detailed_violations}

---

## 🛠️ Action Items

- [ ] Refactor imports in `domain` to remove `infrastructure` dependencies
- [ ] Use `Protocol` interfaces to invert dependencies
- [ ] Ensure all external framework usage is isolated to factory layer
