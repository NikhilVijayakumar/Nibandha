# Module Dependency Report - Template

## Overview
Template for the Module Dependency analysis.

**File**: `module_dependency_report_template.md`

## Structure

```markdown
# Module Dependency Report

**Date:** {date}
**Overall Status:** {status}

---

## 🕸️ Dependency Graph

![Module Dependencies](../assets/images/module_dependencies.png)

---

## 📊 Dependency Summary

| Metric | Value |
| :--- | :---: |
| **Total Modules** | {total_modules} |
| **Total Dependencies** | {total_dependencies} |
| **Circular Dependencies** | {circular_count} |
| **Isolated Modules** | {isolated_count} |

---

## 🔗 Key Dependencies

### Most Imported Modules
{most_imported_table}

### Most Dependent Modules
{most_dependent_table}

---

## ⚠️ Issues

### Circular Dependencies
{cycles_block}

### Isolated Modules
{isolated_block}
```
