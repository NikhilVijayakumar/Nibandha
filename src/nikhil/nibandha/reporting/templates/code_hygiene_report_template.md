---
title: "Code Hygiene Report"
date: "{{ date }}"
grade: "{{ display_grade }}"
grade_color: "{{ grade_color }}"
status: "{{ overall_status }}"
---

# Code Hygiene Report

> [!NOTE]
> **Summary**
>
> - **Grade**: <span style="color:{{ grade_color }}">**{{ display_grade }}**</span>
> - **Status**: {{ overall_status }}
> - **Total Issues**: {{ total_violations }}

## Overview

This report highlights maintenance anti-patterns such as magic numbers, hardcoded paths, and forbidden function usage.

## Detailed Violations

{% if total_violations == 0 %}
> [!TIP]
> **Clean Codebase**
>
> No hygiene issues detected!
{% else %}
### Magic Numbers
{% if magic_numbers %}

: **Table 8.1:** Magic number violations

| S.No | File | Line | Value |
| :---: | :--- | :---: | :--- |
{% for v in magic_numbers -%}
| {{ loop.index }} | `{{ v.file }}` | {{ v.line }} | `{{ v.value }}` |
{% endfor -%}
{% else %}
*No magic numbers detected.*
{% endif %}

### Hardcoded Paths
{% if hardcoded_paths %}

: **Table 8.2:** Hardcoded path violations

| S.No | File | Line | Path |
| :---: | :--- | :---: | :--- |
{% for v in hardcoded_paths -%}
| {{ loop.index }} | `{{ v.file }}` | {{ v.line }} | `{{ v.value }}` |
{% endfor -%}
{% else %}
*No hardcoded paths detected.*
{% endif %}

### Forbidden Functions
{% if forbidden_functions %}

: **Table 8.3:** Forbidden function violations

| S.No | File | Line | Function |
| :---: | :--- | :---: | :--- |
{% for v in forbidden_functions -%}
| {{ loop.index }} | `{{ v.file }}` | {{ v.line }} | `{{ v.value }}` |
{% endfor -%}
{% else %}
*No forbidden functions detected.*
{% endif %}

{% endif %}
