---
title: "Duplication Report"
date: "{{ date }}"
grade: "{{ display_grade }}"
grade_color: "{{ grade_color }}"
status: "{{ overall_status }}"
---

# Code Duplication Report

> [!NOTE]
> **Summary**
>
> - **Grade**: <span style="color:{{ grade_color }}">**{{ display_grade }}**</span>
> - **Status**: {{ overall_status }}
> - **Duplicated Blocks**: {{ total_violations }}

## Overview

Duplication analysis identifies code clones that violate the DRY (Don't Repeat Yourself) principle.

{% if total_violations == 0 %}
> [!TIP]
> **DRY Codebase**
>
> No significant code duplication detected.
{% else %}
> [!WARNING]
> **Duplication Hotspots**
>
> Found **{{ total_violations }}** duplicated code blocks.
{% endif %}

## Duplicated Blocks

{% if duplicates %}
{% for dup in duplicates %}
### Block {{ loop.index }}

**Files involved:**
{% for file in dup.files %}
- `{{ file }}`
{% endfor %}

```text
{{ dup.header }}
```

---
{% endfor %}
{% else %}
*No duplicates found.*
{% endif %}
