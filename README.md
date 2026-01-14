# 📜 Nibandha (निबन्ध)

**Nibandha** is a universal, protocol-based Logger and Storage Manager designed to provide a unified workspace for the AI ecosystem. It serves as the foundational "binding" for applications like **Amsha** (AI Agents) and **Pravaha** (Workflows).

The name comes from the Sanskrit word for "binding" or "record-keeping," reflecting its role in centralizing logs and data outputs into a single, organized structure.

## ✨ Features

* **Unified Root:** All data is centralized under a single `.Nibandha/` directory.
* **App Isolation:** Each application (Amsha, Pravaha, Akashvani) receives its own dedicated namespace and folder structure.
* **Protocol-Based:** Lean design that works with any Python project by adhering to a simple configuration contract.
* **Standardized Logging:** Automatically configures rolling file logs and console output for every registered app.
* **Future-Ready:** Built-in hooks for data versioning and cloud synchronization (MinIO/S3).

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

## 🔧 Configuration

Nibandha can be configured globally using environment variables via a `.env` file:

* `NIBANDHA_ROOT`: Change the root directory name (Default: `.Nibandha`)
* `LOG_LEVEL`: Set global logging level (DEBUG, INFO, ERROR)

---

## 🗺 Roadmap

* [ ] **Data Versioning:** Automated timestamped file naming to prevent overwrites.
* [ ] **Cloud Sync:** Background synchronization of the `.Nibandha` root to **MinIO** or **AWS S3**.
* [ ] **Metrics Export:** Built-in Prometheus exporter for tracking storage usage and error rates.

---
