

### 📂 `.agent/skills/package-maintainer/examples/versioning_strategy.md`

# 🔢 Semantic Versioning (SemVer) Strategy

The Nibandha ecosystem follows the `MAJOR.MINOR.PATCH` format. The **Package-Maintainer** must use this guide to determine the next version in `pyproject.toml`.

## 1. The Format

| Position | Type | Trigger | Example |
| --- | --- | --- | --- |
| **X**.0.0 | **MAJOR** | Incompatible API changes (Breaking) | `0.1.0`  `1.0.0` |
| 0.**X**.0 | **MINOR** | New functionality in a backwards-compatible manner | `1.0.0`  `1.1.0` |
| 0.0.**X** | **PATCH** | Backwards-compatible bug fixes/refactors | `1.1.0`  `1.1.1` |

---

## 2. Decision Matrix for Nibandha

Before updating `pyproject.toml`, evaluate the changes:

### 🔴 MAJOR: Breaking Change

* Renaming a Protocol in `domain/protocols/`.
* Changing the required fields in a `frozen` Pydantic model.
* Deleting or moving a public class (e.g., moving `Archiver` to a different sub-package).

### 🟡 MINOR: Feature Addition

* Adding a new sub-module (e.g., adding `S3Uploader` to the `archiver` module).
* Adding an optional field with a default value to a Pydantic model.
* Adding a new capability to the **Fluent Builder** that doesn't break existing `.build()` calls.

### 🟢 PATCH: Internal Refactor

* Fixing a logic bug that doesn't change the function signature.
* Updating internal logs or **Deep Traceability** IDs.
* Improving performance or security within a class method.

---

## 3. Automation Rule: Version Truth

* **Single Source of Truth:** The version must only be defined in `pyproject.toml`.
* **Dynamic Access:** Every `__init__.py` in the root must use the following pattern to avoid hardcoding:

```python
# src/nikhil/nibandha/__init__.py
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("nikhil-nibandha")
except PackageNotFoundError:
    __version__ = "unknown"

```

---

## 4. Pre-release Tagging

During the "Scaffolding" and "Red Phase," use alpha/beta tags:

* `0.1.0-alpha.1`: Documentation and Tests scaffolded (RED).
* `0.1.0-beta.1`: Implementation complete but pending full E2E audit.
* `0.1.0`: Final release, passed all Sentinel gates.

---
