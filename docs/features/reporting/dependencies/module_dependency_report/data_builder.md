# Module Dependency Report - Data Builder

## Overview
The `ModuleDependencyDataBuilder` uses AST parsing or graph analysis tools (like `pydeps` or custom AST walkers) to build a directed graph of module dependencies.

---

## Analysis Logic

### Dependency Extraction
1. **Scan**: Walk through all `.py` files in `src/`.
2. **Build Module Name**: Convert `src/path/to/file.py` -> `path.to.file`.
3. **Parse Imports**: Extract `import X` and `from X import Y`.
4. **Resolve**: Map imports to internal project modules (ignoring stdlib and 3rd party).

### Graph Analysis
- **Cycles**: Use Tarjan's or similar algorithm to find strongly connected components > size 1.
- **Isolation**: Nodes with in-degree = 0 and out-degree = 0 (excluding root/config).
- **Metrics**: 
  - **Hubs**: High fan-in (many depend on it).
  - **Orphans**: Zero connections.

---

## Output Data Schema (`module_dependency_data.json`)

```json
{
  "date": "2026-01-17",
  "status": "✅ HEALTHY",
  
  "metrics": {
    "total_modules": 9,
    "total_dependencies": 15,
    "circular_dependencies": 0,
    "isolated_modules": 2
  },
  
  "cycles": [
    ["ModuleA", "ModuleB", "ModuleA"]
  ],
  
  "isolated_list": ["Bot", "Utils"],
  
  "key_dependencies": {
    "most_imported": [
      {"module": "Logging", "count": 5}
    ],
    "most_dependent": [
      {"module": "Workflow", "count": 3}
    ]
  },

  "graph_data": { ... } // Optional: adjacency list for visualization
}
```

## Status Determination
- **🔴 FAIL**: One or more circular dependencies detected.
- **✅ HEALTHY**: No cycles. (Isolation might be 🟡 WARN).
