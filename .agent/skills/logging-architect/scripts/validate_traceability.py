import os
import re
import sys
from pathlib import Path


class TraceabilityValidator:
    def __init__(self, module_name: str, root_dir: str = "."):
        self.module_name = module_name
        self.root = Path(root_dir)
        # Pattern to find [XX-UT-001] style IDs
        self.id_pattern = re.compile(r'([A-Z]{2}-(?:UT|E2E)-\d{3})')

    def get_blueprint_ids(self) -> set:
        """Extracts all required IDs from the documentation."""
        ids = set()
        doc_path = self.root / "docs" / "test" / self.module_name
        if not doc_path.exists():
            return ids

        for doc_file in doc_path.glob("*.md"):
            content = doc_file.read_text()
            ids.update(self.id_pattern.findall(content))
        return ids

    def get_implemented_ids(self) -> set:
        """Extracts all IDs actually used in logger calls within src/."""
        ids = set()
        src_path = self.root / "src" / self.module_name
        if not src_path.exists():
            return ids

        for py_file in src_path.glob("**/*.py"):
            content = py_file.read_text()
            # Specifically look for IDs within logger calls
            logger_matches = re.findall(r'logger\.\w+\(f?[\'"].*?(\[?[A-Z]{2}-(?:UT|E2E)-\d{3}\]?).*?[\'"]', content)
            for match in logger_matches:
                # Clean brackets if present
                clean_id = match.replace("[", "").replace("]", "")
                ids.add(clean_id)
        return ids

    def validate(self):
        print(f"🔍 Validating Traceability for: {self.module_name}")
        blueprint_ids = self.get_blueprint_ids()
        implemented_ids = self.get_implemented_ids()

        missing = blueprint_ids - implemented_ids

        if not blueprint_ids:
            print("⚠️ No IDs found in documentation. Is the blueprint scaffolded?")
            return False

        if missing:
            print(f"❌ TRACEABILITY GAP DETECTED")
            print(f"The following IDs exist in docs but are NOT logged in src:")
            for m_id in sorted(missing):
                print(f"  - {m_id}")
            return False

        print(f"✅ SUCCESS: All {len(blueprint_ids)} blueprint IDs are traceable in source code.")
        return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_traceability.py [module_name]")
        sys.exit(1)

    validator = TraceabilityValidator(sys.argv[1])
    success = validator.validate()
    sys.exit(0 if success else 1)