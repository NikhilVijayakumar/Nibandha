# Summary Report - Template

## Overview
Dashboard template.

**File**: `summary_report_template.md`

## Structure

```markdown
# Pravaha Test & Quality Report

**Generated:** {date}
**Overall Status:** {overall_status}

---

## 📊 Quick Summary

{summary_table}

---

## 🧪 Test Reports

### Unit Tests
{unit_summary_block}
![Unit Outcomes](assets/images/unit_outcomes.png)
📄 [Detailed Unit Report]({link_unit})

### E2E Tests
{e2e_summary_block}
![E2E Status](assets/images/e2e_status.png)
📄 [Detailed E2E Report]({link_e2e})

---

## 🔍 Quality Reports

### Type Safety
{type_safety_summary_block}
![Type Errors](assets/images/type_errors_by_module.png)
📄 [Detailed Report]({link_type_safety})

... (other reports)

---

## 📂 Report Structure
...
```
