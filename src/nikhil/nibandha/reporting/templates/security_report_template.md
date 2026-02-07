---
title: "Security Report (SAST)"
date: "{{ date }}"
grade: "{{ display_grade }}"
grade_color: "{{ grade_color }}"
status: "{{ overall_status }}"
---

# Security Report

> [!IMPORTANT]
> **Summary**
>
> - **Grade**: <span style="color:{{ grade_color }}">**{{ display_grade }}**</span>
> - **Status**: {{ overall_status }}
> - **Total Issues**: {{ total_violations }}

## Overview

Static Application Security Testing (SAST) results from **Bandit**.

![Security Severity](../assets/images/quality/security_severity.png)
*(Severity Distribution)*

![Security Hotspots](../assets/images/quality/security_hotspots.png)
*(Top Modules with Violations)*

{% if "PASS" in overall_status %}
> [!TIP]
> **Secure**
>
> No High/Medium severity vulnerabilities detected.
{% else %}
> [!WARNING]
> **Vulnerabilities Detected**
>
> Found **{{ high_count }}** High and **{{ medium_count }}** Medium severity issues.
{% endif %}

## Vulnerabilities

{% if error_details %}
> [!CAUTION]
> **Execution Error**
>
> {{ error_details }}
{% endif %}

{% if issues %}
{% for issue in issues %}
### [{{ issue.issue_severity }}] {{ issue.test_id }}: {{ issue.test_name }}

- **File**: `{{ issue.filename }}` (Line {{ issue.line_number }})
- **Confidence**: {{ issue.issue_confidence }}

```python
{{ issue.code }}
```

> {{ issue.issue_text }}

---
{% endfor %}
{% elif not error_details %}
*No issues found.*
{% endif %}
