# Unit Test Scenarios: Archiver Logic

**Prefix:** `AR` | **Location:** `docs/test/archiver/unit_test_scenarios.md`

## 1. Happy Path (Success Cases)

Focuses on the core functional requirements working under ideal conditions.

| ID | Scenario | Input | Expected Outcome |
| --- | --- | --- | --- |
| **AR-UT-001** | **Standard Compression** | 10MB Plaintext Log | Returns byte stream; size reduction > 50%. |
| **AR-UT-002** | **Under Quota Check** | Total size: 500MB, Limit: 1GB | Returns `False`; no cleanup triggered. |
| **AR-UT-003** | **Multiple File Sort** | List of 5 files with varied timestamps | Returns list sorted from **Oldest to Newest**. |

## 2. Corner Cases (Boundary Logic)

Verifies the logic at the "edges" of your Pydantic models and math.

| ID | Scenario | Input | Expected Outcome |
| --- | --- | --- | --- |
| **AR-UT-004** | **Zero Byte File** | Empty `.log` file | Returns valid (but empty) `.zip` without error. |
| **AR-UT-005** | **Exact Quota Match** | Total size: 1024MB, Limit: 1024MB | Returns `False`; cleanup triggers only on **breach**. |
| **AR-UT-006** | **Max Compression Level** | Level 9 setting | Returns highest possible compression ratio. |

## 3. Security & Validation (Guardrails)

Ensures the module cannot be used to perform unauthorized operations.

| ID | Scenario | Input | Expected Outcome |
| --- | --- | --- | --- |
| **AR-UT-007** | **Path Traversal Shield** | Input path: `../../etc/passwd` | Raises `SecurityViolationError` or sanitizes path. |
| **AR-UT-008** | **Frozen Config Check** | Attempt to modify `max_age_days` at runtime | Raises `ValidationError` (Pydantic Frozen=True). |
| **AR-UT-009** | **Symlink Protection** | Source file is a Symlink | Logic ignores or raises error; prevents out-of-bounds reading. |

## 4. Error Handling (Unhappy Path)

Verifies how the logic reacts to internal data inconsistencies.

| ID | Scenario | Input | Expected Outcome |
| --- | --- | --- | --- |
| **AR-UT-010** | **Missing Source** | Reference to non-existent file ID | Returns `NotFoundError` instead of crashing. |
| **AR-UT-011** | **Unsupported Format** | Setting `archive_format="rar"` | Raises `ValidationError` (Value not in Allowed list). |

---

### 💡 Why this is the "Gold Standard"

* **Comprehensive Coverage:** It covers **Happy**, **Edge**, **Security**, and **Failure** paths.
* **Strict IDs:** Notice the IDs continue sequentially (**AR-UT-001** through **AR-UT-011**).
* **Zero Implementation Bias:** It describes the *logic* (e.g., "Sorts oldest to newest") without mentioning Python specific functions like `.sort()` or `sorted()`.
* **Security Conscious:** It explicitly lists **Path Traversal** and **Symlink** checks, which are critical for a library dealing with file systems.
