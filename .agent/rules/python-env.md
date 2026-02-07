# Python Environment & Structure Rules

## Environment Management
- **Virtual Environment:** Always use the local virtual environment located at `./venv` (or `./.venv`). 
- **Execution:** Before running any Python command (pytest, scripts, etc.), ensure it is executed via the venv (e.g., `./venv/Scripts/python.exe` or `source venv/bin/activate`).
- **Dependencies:** DO NOT just install packages. Always update `pyproject.toml` first and then use your package manager (e.g., `pip`, `poetry`, or `pdm`) to sync.

## Project Structure
- **Source Root:** The source code is NOT always in `src/`. 
- **Config Discovery:** Always read `pyproject.toml` to find the `tool.setuptools.packages` or `tool.poetry.packages` definition to identify the correct source directory.
- **Imports:** Respect the package structure defined in `pyproject.toml` when suggesting imports or creating new modules.