# 14. Encoding Verification Report

**Generated:** {{ date }}
**Status:** {{ overall_status }}
**Violations:** {{ total_violations }}
**Files Checked:** {{ checked_count }}
**Grade:** <span style="color:{{ grade_color }}; font-size: 1.5em; font-weight: bold;">{{ display_grade }}</span>

## Overview
This report verifies that all source files (`.py`, `.md`, `.json`, etc.) are valid **UTF-8** and do not contain **Byte Order Marks (BOM)**, which can cause cross-platform compatibility issues (Windows vs Linux).

### Summary
: **Table 14.1:** Encoding check summary

| S.No | Category | Status | Count |
| :---: | :--- | :---: | :--- |
| 1 | **Non-UTF-8 Files** | {{ non_utf8_status }} | {{ non_utf8_count }} |
| 2 | **BOM Detected** | {{ bom_status }} | {{ bom_count }} |

---

## ❌ Violations

### Non-UTF-8 Files (Encoding Error)
{% if non_utf8 %}
Files that could not be decoded as strict UTF-8. These files likely use Windows-1252 or Latin-1 encoding.

| S.No | File | Error |
| :---: | :--- | :--- |
{% for v in non_utf8 %}
| {{ loop.index }} | `{{ v.file }}` | {{ v.error }} |
{% endfor %}
{% else %}
*No encoding errors found. All files are valid UTF-8.*
{% endif %}

### Byte Order Mark (BOM) Detected
{% if bom_present %}
Files containing a BOM signature (`\xef\xbb\xbf`). This is common on Windows (Notepad) but problematic for Linux scripts and tools.

| S.No | File | Error |
| :---: | :--- | :--- |
{% for v in bom_present %}
| {{ loop.index }} | `{{ v.file }}` | {{ v.error }} |
{% endfor %}
{% else %}
*No BOM signatures found.*
{% endif %}

---

## ✅ Recommendation
- **Non-UTF-8**: Open file in editor (VS Code/PyCharm) and "Save with Encoding" -> UTF-8.
- **BOM**: Save file as UTF-8 (NO BOM). In Python, use `encoding='utf-8'` explicitly when reading/writing.
