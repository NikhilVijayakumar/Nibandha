# Sandbox Test Report: {{ test_name }}

**Date**: {{ timestamp }}
**Result**: {{ result }}

## Description
{{ description }}

## Input
**File**: `{{ input_filename }}`

```{{ input_format }}
{{ input_content }}
```

## Output

### Expected
{{ expected_output_desc }}

### Actual
{{ actual_output_desc }}

```json
{{ actual_output_json }}
```

{% if error_log %}
## Errors
```text
{{ error_log }}
```
{% endif %}
