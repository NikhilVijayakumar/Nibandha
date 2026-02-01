# Module Dependency Report - Visualization

## Charts

### 1. Module Dependency Graph (`module_dependencies.png`)

**Type**: Directed Graph (Node-Link Diagram)
**Purpose**: Visualize how modules interact.

**Tools**: `graphviz`, `networkx`, or `pydeps`.

**Styling**:
- **Nodes**: Modules (rectangles/ellipses).
- **Edges**: Dependencies (arrows).
- **Hubs**: Larger size for high degree.
- **Cycles**: Highlighted in Red.

---

## Customization

- **Provider Override**: Clients can use their own graph layout engine.
- **Output**: `module_dependencies.png` in assets folder.
