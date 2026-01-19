import os
import sys
from pathlib import Path


def validate_implementation_purity(file_path: Path):
    """Checks for violations of the Clean-Implementation standards."""
    content = file_path.read_text()
    violations = []

    # Check for relative imports
    if "from ." in content:
        violations.append("Relative import found (violation of Absolute Import rule).")

    # Check for print statements
    if "print(" in content:
        violations.append("print() statement found (violation of Zero-Print policy).")

    # Check for nested functions
    if "    def " in content and not content.strip().startswith("class"):
        violations.append("Nested function or non-class method detected.")

    if violations:
        print(f"❌ Standards Violation in {file_path}:")
        for v in violations: print(f"  - {v}")
        return False
    return True


if __name__ == "__main__":
    if len(sys.argv) > 1:
        validate_implementation_purity(Path(sys.argv[1]))