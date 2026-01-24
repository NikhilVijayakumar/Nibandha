
### 📂 `.agent\skills\nibandha-manager\examples\nibandha_manager_trigger_logic.md`

# Nibandha Manager Orchestration: Trigger & Workflow (3-Stage TDD)

## 1. Activation Event

**User Input:** `"Nibandha Manager, create [Module_Name]"`

## 2. Decision Logic (The "Brain")

Before acting, the Manager identifies complexity and enforces **Stage 0 (Environmental Sovereignty)**:

1. **Venv Check:** Locate `./.venv/` and use the local binary for all subprocesses.
2. **Source Discovery:** Parse `pyproject.toml` to identify the absolute `{root}` prefix.
3. **Complexity Mapping:**
* **Standard:** Single file implementation.
* **Complex:** Scaffolds sub-module directory structures.



---

## 3. The Execution Sequence (TDD Order)

| Order | Agent | Primary Action | Success Criteria |
| --- | --- | --- | --- |
| **Stage 0** | **Environment** | Venv & Root Validation | `.venv` exists; Root prefix identified. |
| **Stage 1** | **Doc-Architect** | Platform-Agnostic Blueprint | Blueprint exists with `XX-UT-00X` IDs. |
| **Stage 2** | **Test-Scaffolder** | Generate **failing** test stubs | `tests/` mirrors Blueprint IDs exactly. |
| **Stage 3** | **Clean-Impl** | Logic + Logging + Config | Passes tests. Absolute Imports enforced. |

---

## 4. Example Output (Agent Log)

*Visualizing the execution logic and environmental locking:*

> **NIBANDHA MANAGER ACTIVATED: Creating module 'AuthService'**
> 🌍 **Stage 0: Environment**... VERIFIED (Root: `nikhil/nibandha` | Interpreter: `./.venv/bin/python`).
> 🔄 **Stage 1: Doc-Architect**... COMPLETED (Blueprint: `docs/modules/auth_service/README.md`).
> 🔄 **Stage 2: Test-Scaffolder**... COMPLETED (8 failing stubs generated in `tests/auth_service/`).
> 🔄 **Stage 3: Clean-Implementation**... COMPLETED (8/8 tests PASS | Zero-Print Enforced).
> ✅ **Nibandha Manager:** Module 'AuthService' is verified and ready for deployment.

---

