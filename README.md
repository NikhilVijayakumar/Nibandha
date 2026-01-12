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
