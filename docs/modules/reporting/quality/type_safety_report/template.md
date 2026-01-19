# Type Safety Report - Template

## Overview
The template defines the structure of the Markdown report generated for Type Safety output.

**File**: `type_safety_report_template.md`

---

## Structure

```markdown
# Type Safety Report

**Date:** {date}
**Tool:** {tool}
**Status:** {status}

---

## 📊 Summary

| Metric | Value |
| :--- | :---: |
| **Total Errors** | {total_errors} |
| **Status** | {status} |

---

## 🛡️ Type Coverage by Module

{module_table}

---

## 📉 Error Distribution

![Type Errors by Module](../assets/images/type_errors_by_module.png)

---

## 🚫 Critical Type Errors

<details>
<summary>Click to expand error details</summary>

```
{critical_errors_block}
```

</details>

---

## 🛠️ Action Items

- [ ] Add missing type hints to function signatures
- [ ] Resolve `Any` types in strict modules
- [ ] Add return type annotations where missing
```

---

## Available Keys

| Key | Description | Example |
| :--- | :--- | :--- |
| `{date}` | Date of generation | 2026-01-17 |
| `{tool}` | Command used | `mypy --strict` |
| `{status}` | Overall status emoji | 🔴 FAIL |
| `{total_errors}` | Integer count | 213 |
| `{module_table}` | Formatted markdown table of modules | |
| `{critical_errors_block}` | Raw text of errors | src/...: error: ... |

---

## Customization
Clients can override this template to:
- Change the header/footer.
- Remove the `<details>` block if they prefer only summaries.
- Add specific instructions for their team in "Action Items".
