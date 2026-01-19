# Type Safety Report - Visualization

## Overview
Visualizations for Type Safety focus on identifying hotspots in the codebase where type errors are concentrated.

---

## Charts

### 1. Type Errors by Module (`type_errors_by_module.png`)

**Type**: Bar Chart (Horizontal or Vertical)
**Purpose**: Show which modules have the most technical debt regarding type safety.

**Data Source**: `errors_by_module` dictionary from JSON.
- **X-Axis**: Module Names (e.g., Storage, Workflow, Auth)
- **Y-Axis**: Error Count

**Styling**:
- **Color**: Red for high errors, fading to orange/yellow.
- **Labels**: Show exact count on top/beside bars.
- **Order**: Sorted descending by error count.

---

## Future Visualizations (Potential)

### 2. Error Categories (`error_categories.png`)
**Type**: Pie Chart / Donut Chart
**Purpose**: Show the distribution of error types (e.g., `import-untyped` vs `no-any-return`).
**Why**: Helps decide if the issue is missing libs (infrastructure) or bad typing (code quality).

---

## Customization

Clients implementing a custom `VisualizationProvider` for type safety should:
1. Implement `generate_type_safety_charts(data, output_dir)`.
2. Generate at least `type_errors_by_module.png` as referenced in the template.
3. Return `{"type_errors_by_module": "path/to/img.png"}`.
