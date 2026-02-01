# Complexity Report - Template

## Overview
Markdown template for the Complexity Report.

**File**: `complexity_report_template.md`

---

## Structure

```markdown
# Complexity Report

**Date:** {date}
**Status:** {status}

---

## 📊 Summary

| Metric | Value |
| :--- | :---: |
| **Total Violations** | {total_violations} |

---

## 📦 Module Breakdown

{module_breakdown}

---

## 📉 Distribution

![Complexity Distribution](../assets/images/complexity_distribution.png)

---

## 🚨 Top Offenders

| Function | Score | Module | Location |
| :--- | :---: | :--- | :--- |
{top_offenders_rows}

---

## 🛠️ Action Items

- [ ] Refactor functions with complexity > 10
- [ ] Split large modules
```

## Keys
- `{date}`
- `{status}`
- `{total_violations}`
- `{module_breakdown}` (Table)
- `{top_offenders_rows}` (Table rows for top complex functions)
