# Complexity Report - Visualization

## Charts

### 1. Complexity Distribution (`complexity_distribution.png`)

**Type**: Histogram or Bar Chart
**Purpose**: Show how many functions fall into different complexity buckets if data allows, OR show violations per module.

**Data Source**: `violations_by_module`
- **X-Axis**: Module
- **Y-Axis**: Count of complexity violations

**Alternate**: If we only have violations, a bar chart of "Violations per Module" is standard.

---

## Customization

- **Input**: `data['violations_by_module']`
- **Output**: key `complexity_distribution` mapping to png path.
