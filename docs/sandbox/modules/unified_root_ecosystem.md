
# Unified Root: Ecosystem Guide

This guide explains how to configure `UnifiedRoot` for complex application ecosystems where a single Main Application (e.g., `Pravaha`) manages resources for itself and its dependencies (e.g., `Nibandha`, `Amsha`).

## The "Single Config" Reality

In a real deployment, there is only **one** `AppConfig` — the one belonging to the running application. Libraries do not load their own `AppConfig` files at runtime; they rely on the host application's environment.

To support multi-library folder structures (e.g., separate log folders for app and libs), use the **Custom Structure** feature.

## Recommended Structure

We recommend a flat, organized structure under the Unified Root:

```
.Pravaha/
├── app/               # Main Application Resources
│   ├── logs/
│   ├── Report/
│   └── data/
├── nibandha/          # Library A Resources
│   ├── logs/
│   └── cache/
├── amsha/             # Library B Resources
│   └── logs/
└── config/            # Shared Runtime Config (Pravaha's)
```

## Configuration Example

To achieve the above structure, configure your Main Application (e.g., Pravaha) as follows:

```json
{
  "name": "Pravaha",
  "unified_root": {
    "name": ".Pravaha",
    "custom_structure": {
      "app": {
        "data": {},
        "cache": {}
      },
      "nibandha": {
        "logs": {},
        "cache": {}
      },
      "amsha": {
        "logs": {}
      }
    }
  },
  "logging": {
    "log_dir": ".Pravaha/app/logs"     // Explicitly point Main App logs to app/
  },
  "reporting": {
    "output_dir": ".Pravaha/app/Report" // Explicitly point Main App reports to app/
  }
}
```

## How It Works

1.  **Unified Root**: Creates `.Pravaha/`.
2.  **Explicit Paths**: `logging` and `reporting` config directs the Main App's primary outputs to `.Pravaha/app/`.
3.  **Custom Structure**: The `custom_structure` block creates the skeleton for all other folders (`nibandha/`, `amsha/`) directly under `.Pravaha/`.
4.  **Library Usage**: Libraries should be configured (via their specific init APIs) to write to these pre-created folders (e.g., `Nibandha(log_dir=".Pravaha/nibandha/logs")`).

## Validation

You can verify this behavior using the sandbox test:
`tests/sandbox/unified_root/ecosystem/test_practical_single_config.py`
