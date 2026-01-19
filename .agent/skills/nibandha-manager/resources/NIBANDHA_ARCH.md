### 📂 `NIBANDHA_ARCH.md`

# 🏛️ Nibandha System Architecture

**Version:** 1.1.0

**Status:** Canonical (Source of Truth)

**Philosophy:** TDD-First, Platform-Agnostic, Zero-Print, Deep Traceability.

---

## 1. The Foundational Three (TDD Workflow)

The **Sentinel** orchestrates development in a strict sequence. Every stage must be validated by the `nibandha_doctor` before the next begins.

| Stage | Agent | Mission | Primary Artifacts |
| --- | --- | --- | --- |
| **1. Design** | **Doc-Architect** | Create platform-neutral blueprints & Schemas. | `docs/modules/`, `docs/test/` |
| **2. Test** | **Test-Scaffolder** | Generate failing test stubs (RED Phase). | `tests/{module}/` |
| **3. Build** | **Clean-Impl** | Implement Logic + Logging + Config (GREEN Phase). | `src/{module}/` |

---

## 2. Technical & Logging Standards

Every agent must adhere to these standards to ensure the library is maintainable and debuggable.

### 🛠️ Core Implementation Rules

* **Absolute Imports:** No relative imports (`from ..logic`). Use `from nibandha.module.logic`.
* **Atomic Classes:** **One Class, One File.** Keep logic focused.
* **Data Integrity:** Use **Pydantic** (`frozen=True`, `strict=True`) for all models.
* **Interface Over Implementation:** Prioritize **Protocols** to remain platform-agnostic.

### 📝 Deep Traceability (Logging)

* **Zero-Print Policy:** Absolute ban on `print()`.
* **Contextual Loggers:** Initialize loggers using `__package__ + "." + __class__.__name__`.
* **Blueprint Mapping:** Every core logic gate must log its **Blueprint ID** (e.g., `logger.info("[AR-UT-001] Initializing...")`).
* **Safe Init:** No side-effects (file/folder creation) during module import.

---

## 3. Directory Topology

A mirrored structure ensures that for every feature, there is a corresponding spec and test.

```text
nibandha/
├── docs/                # Stage 1: The Blueprints (Language Neutral)
│   ├── modules/         # Functional Specs & Data Schemas
│   └── test/            # Scenarios (UT/E2E) with unique IDs
├── tests/               # Stage 2: The Verification (Pytest)
│   └── {module}/        # 8-file TDD pattern
├── src/                 # Stage 3: The Reality (Python/Kotlin/TS)
│   └── {module}/        # Clean logic + Traceable logging
└── .agent/              # The Intelligence (Sentinel, Skills, Doctor)

```

---

## 4. Test ID & Mapping

* **Format:** `[PREFIX]-[TYPE]-[ID]` (e.g., `FR-UT-001`).
* **Traceability:** Every ID defined in `docs/test/` must exist as a test function in `tests/` and a log entry in `src/`.

---

## 5. Security & Orchestration

1. **Atomic Operations:** Use temporary file writes and renames to prevent data corruption.
2. **State-Awareness:** The Sentinel uses `skip_if_exists` logic to resume failed or partial builds.
3. **Refactor-Only:** The Sentinel does not fix code; it returns errors to the implementation agent for refactoring.

---

### 💡 Agent Handover Protocol

Before starting any work, the agent must check the **Nibandha Doctor**.

* **Green:** Proceed to next stage.
* **Red:** Trigger **Recovery Protocol** (Rollback or Refactor).
