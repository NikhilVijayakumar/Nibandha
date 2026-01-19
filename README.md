# 📜 Nibandha (निबन्ध)

**Nibandha** is a universal, protocol-based Logger and Storage Manager designed to provide a unified workspace for the AI ecosystem. It serves as the foundational "binding" for applications like **Amsha** (AI Agents) and **Pravaha** (Workflows).

The name comes from the Sanskrit word for "binding" or "record-keeping," reflecting its role in centralizing logs and data outputs into a single, organized structure.

## ✨ Features

* **Unified Root:** All data is centralized under a single `.Nibandha/` directory.
* **App Isolation:** Each application (Amsha, Pravaha, Akashvani) receives its own dedicated namespace and folder structure.
* **Protocol-Based:** Lean design that works with any Python project by adhering to a simple configuration contract.
* **Standardized Logging:** Automatically configures named loggers with file and console handlers.
* **Log Rotation & Archival:** Size-based and time-based rotation with automatic cleanup.
* **Quality Reporting:** Built-in comprehensive quality reports (unit, E2E, dependencies, complexity).
* **Zero-Config Default:** Works out-of-the-box with sensible defaults.
* **Fully Customizable:** Every aspect can be overridden via config files or programmatic API.

---

## 🎯 Design Principles

1. **Zero-Config Default**: Works out-of-the-box with sensible defaults - minimal code to get started
2. **Fully Customizable**: Every aspect can be overridden by clients when needed
3. **Protocol-Based**: Lean design following simple configuration contracts
4. **Application-Centric**: Each app controls its own folder structure and settings
5. **Production-Ready**: Built for reliability with comprehensive error handling

### Benefits

**For Developers:**
- ✅ Quick Integration - Minimal code to get started
- ✅ Predictable Structure - Standard directory layout
- ✅ Full Control - Override anything when needed

**For Operations:**
- ✅ Centralized Logs - All apps in one `.Nibandha/` directory
- ✅ Automatic Rotation - Prevents disk space issues
- ✅ Easy Backup - Single directory to backup/sync

---

## 📂 The Workspace Structure

When you initialize Nibandha, it creates a standardized hierarchy:

```text
.Nibandha/
├── Amsha/                  # AI Agent Workspace
│   ├── logs/               # amsha.log
│   └── output/
│       ├── final/
│       └── intermediate/
├── Pravaha/                # API & Workflow Workspace
│   ├── logs/               # pravaha.log
│   ├── workflow/
│   └── config/
└── [OtherApp]/             # Universal support for any new project
    └── logs/

```

---

## 🚀 Installation

Add Nibandha to your project via `pyproject.toml`:

```toml
[tool.poetry.dependencies]
nibandha = { git = "https://github.com/your-username/nibandha.git", branch = "main" }

```

Or install via pip:

```bash
pip install git+https://github.com/your-username/nibandha.git

```

---

## 🛠 Usage

### 1. Basic Integration (e.g., in Pravaha)

```python
from nikhil.nibandha import Nibandha, AppConfig
from pathlib import Path

# Define the application identity and custom folders
config = AppConfig(
    name="Pravaha",
    custom_folders=[
        "workflow/details",
        "workflow/run",
        "config"
    ]
)

# Bind the app to the Nibandha workspace
nb = Nibandha(config).bind()

# Start logging immediately
nb.logger.info("Pravaha has been bound to Nibandha.")

```

### 2. Implementation in Amsha (CrewAI)

```python
from nikhil.nibandha import Nibandha, AppConfig

amsha_nb = Nibandha(AppConfig(
    name="Amsha",
    custom_folders=["output/final/output", "output/intermediate/output"]
)).bind()

amsha_nb.logger.warning("Agent task initiated.")

```

---

## 🔄 Log Rotation and Archival

Nibandha supports automatic log rotation with timestamped files, archival, and cleanup.

### First-Time Setup

When you call `bind()` for the first time, Nibandha will prompt you for rotation settings:

```python
from nibandha import Nibandha, AppConfig

config = AppConfig(
    name="Pravaha",
    custom_folders=["workflow/details", "workflow/run", "config"]
)

# First run - shows interactive prompts
nb = Nibandha(config).bind()

# Output:
# 📋 Log Rotation Configuration
# ==================================================
# Enable log rotation? (y/n) [n]: y
# Max log size in MB before rotation [10]: 50
# Rotation interval in hours [24]: 24  
# Archive retention in days [30]: 30
# ✅ Configuration saved to .Nibandha/config/rotation_config.yaml
```

### Subsequent Runs

Configuration is cached, so no prompts on subsequent runs:

```python
# No prompts - uses cached config
nb = Nibandha(config).bind()
```

### Directory Structure

When rotation is enabled:

```text
.Nibandha/
├── config/
│   └── rotation_config.yaml   # Cached settings
├── Pravaha/
│   └── logs/
│       ├── data/               # Active timestamped logs
│       │   ├── 2026-01-14_04-30-00.log
│       │   └── 2026-01-14_16-45-00.log
│       └── archive/            # Archived logs  
│           ├── 2026-01-10_10-00-00.log
│           └── 2026-01-12_08-15-00.log
```

### Rotation Triggers

Logs rotate when **either** condition is met:
- **Size limit** - Log reaches configured max size (e.g., 50MB)
- **Time limit** - Log reaches configured interval (e.g., 24 hours)

### Using Rotation Utilities

```python
# In your application or scheduled task:

# Check if rotation is needed
if nb.should_rotate():
    nb.rotate_logs()  # Creates new timestamped log, archives old one

# Periodically clean up old archives
deleted = nb.cleanup_old_archives()
print(f"Cleaned up {deleted} old archives")
```

### Scheduling Options

**Linux/Mac - Cron:**
```bash
# Check and rotate every hour
0 * * * * /usr/bin/python3 /path/to/rotate_script.py
```

**Windows - Task Scheduler:**
Create a scheduled task that runs your rotation script daily.

### Manual Configuration

Skip prompts by creating the config file manually:

```yaml
# .Nibandha/config/rotation_config.yaml
enabled: true
max_size_mb: 100              # Rotate at 100MB
rotation_interval_hours: 168  # OR every week (168 hours)
archive_retention_days: 90    # Keep 90 days of archives
log_data_dir: "logs/data"
archive_dir: "logs/archive"
timestamp_format: "%Y-%m-%d_%H-%M-%S"
```

---

## 📊 Quality Reporting

Nibandha includes a comprehensive reporting module that generates professional quality reports for your project.

### Installation

Install Nibandha with reporting extras:

```bash
pip install nibandha[reporting]
```

### Quick Start

Generate all reports with minimal configuration:

```python
from nibandha.reporting import ReportGenerator

# Initialize generator
generator = ReportGenerator(
    output_dir=".Nibandha/Report",
    docs_dir="docs/test"
)

# Generate ALL reports (unit, E2E, quality, dependencies)
generator.generate_all()
```

### Custom Configuration

Customize paths and specify targets:

```python
from nibandha.reporting import ReportGenerator

generator = ReportGenerator(
    output_dir="/path/to/custom/output",
    docs_dir="docs/test",
    template_dir="/path/to/custom/templates"  # Optional
)

# Specify targets for each report type
generator.generate_all(
    unit_target="tests/unit",           # Path to unit tests
    e2e_target="tests/e2e",             # Path to E2E tests  
    package_target="src/your/package"   # Package to analyze
)
```

### Using the Script

You can also use the provided script:

```bash
python scripts/generate_unified_report.py
```

### Reports Generated

After running `generate_all()`, you'll find these reports in your `output_dir`:

1. **`overview.md`** - Combined overview with all metrics
2. **`unit_report.md`** - Unit test results with coverage
3. **`e2e_report.md`** - E2E scenario results
4. **`type_safety_report.md`** - MyPy static type checking
5. **`complexity_report.md`** - Code complexity metrics
6. **`architecture_report.md`** - Import structure compliance
7. **`quality_overview.md`** - Overall quality summary
8. **`module_dependency_report.md`** - Internal module dependencies
9. **`package_dependency_report.md`** - PyPI package analysis

All reports include visualizations (charts) and are saved as Markdown files.

For detailed documentation, see [docs/modules/reporting.md](docs/modules/reporting.md).

---

## 🔧 Configuration

Nibandha can be configured globally using environment variables via a `.env` file:

* `NIBANDHA_ROOT`: Change the root directory name (Default: `.Nibandha`)
* `LOG_LEVEL`: Set global logging level (DEBUG, INFO, ERROR)

---

## 📚 Documentation

For comprehensive guides and detailed documentation, see:

- **[Module Documentation](docs/modules/README.md)** - Complete module reference
  - [Overview](docs/modules/overview.md) - Architecture and core principles
  - [Unified Root](docs/modules/unified-root.md) - Workspace structure details
  - [Logging Module](docs/modules/logging.md) - Logger internals and configuration
  - [Log Rotation](docs/modules/log-rotation.md) - Rotation setup and troubleshooting
  - [Reporting Module](docs/modules/reporting.md) - Quality reporting system
  - [Configuration](docs/modules/configuration.md) - Config system reference
  - [Client Integration](docs/modules/client-integration.md) - Integration examples

- **[Testing Strategy](docs/test/testing_strategy.md)** - Testing conventions and standards
- **[Test Scenarios](docs/test/)** - Detailed test scenario documentation

---

## 🗺 Roadmap

* [ ] **Data Versioning:** Automated timestamped file naming to prevent overwrites.
* [ ] **Cloud Sync:** Background synchronization of the `.Nibandha` root to **MinIO** or **AWS S3**.
* [ ] **Metrics Export:** Built-in Prometheus exporter for tracking storage usage and error rates.

---
