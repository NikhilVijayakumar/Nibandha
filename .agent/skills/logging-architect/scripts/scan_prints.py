import sys
import re
from pathlib import Path

def audit_zero_print(file_path: str):
    content = Path(file_path).read_text()
    # Matches print() but ignores comments
    matches = re.findall(r'^(?!#)\s*print\(', content, re.MULTILINE)
    if matches:
        print(f"❌ Violation: Found {len(matches)} print statements in {file_path}")
        sys.exit(1)
    print(f"✅ {file_path} follows Zero-Print Policy.")

if __name__ == "__main__":
    audit_zero_print(sys.argv[1])