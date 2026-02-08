# Nibandha Sandbox Architecture

## Philosophy
The **Sandbox** is a specialized testing environment designed to verify the "real-world" behavior of the application without affecting the developer's actual environment. Unlike standard unit tests that mock everything, the sandbox:
1.  **Uses Real I/O**: It actually writes files, generates reports, and creates logs.
2.  **Isolates Artifacts**: All output is directed to a dedicated `.sandbox` directory, keeping the project clean.
3.  **Simulates Environments**: It allows us to test behavior under different conditions (e.g., missing configuration files, different OS paths) that are hard to replicate in unit tests.

## Why do we need it?
### 1. Verification of "Side Effects"
Nibandha is a tool that *creates things* (reports, logs, directories). Unit tests often mock these file system operations. The Sandbox verifies that:
- Files are actually created.
- Directories are structured correctly.
- Content is written as expected (e.g., JSON is valid, Markdown renders).

### 2. Configuration Robustness
Users run Nibandha in diverse environments. The Sandbox allows us to test:
- **Portability**: ensuring paths work on Windows, Linux, and macOS.
- **Fallbacks**: Verifying that the system behaves correctly when optional settings (like `template_dir`) are missing.
- **Partial Fallback**: Ensuring that invalid fields (e.g., wrong types) are individually defaulted while valid settings are preserved ("Mixed Validity").
- **Error Handling**: ensuring users get helpful error messages for bad config, rather than stack traces.

### 3. Artifact Persistence
Sandbox artifacts (logs, generated reports) are preserved after the test run (until the next run). This allows developers to manually inspect the output to "see what the user sees."

## How it Works
1.  **Test Execution**: Tests are located in `tests/sandbox`.
2.  **Runner**: The `scripts/run_sandbox.py` script executes these tests.
3.  **Cleanup**: Before a test module runs, its corresponding folder in `.sandbox` is wiped clean to ensure validity.
4.  **Generation**: The tests run and write outputs to `.sandbox/<module>/<test_name>`.
5.  **Verification**: Assertions successfully validate the generated files.

## Usage
Run the sandbox tests using the dedicated runner script: **`scripts/run_sandbox.py`**

### Commands
-   **List Modules**: See available test modules.
    ```bash
    python scripts/run_sandbox.py --list
    ```
-   **Run All**: Execute all sandbox tests.
    ```bash
    python scripts/run_sandbox.py
    ```
-   **Run Specific Module**: Run only tests for a specific feature (e.g., configuration).
    ```bash
    python scripts/run_sandbox.py configuration
    ```
-   **Clean & Run**: Wipe previous artifacts for a fresh start (Recommended).
    ```bash
    python scripts/run_sandbox.py configuration --clean
    ```

## Directory Structure
- `tests/sandbox/`: Source code for sandbox tests.
- `.sandbox/`: Generated output artifacts (Git-ignored).
