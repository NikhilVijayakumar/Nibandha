import shutil
import subprocess
import logging
import re
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger("nibandha.reporting.quality.duplication")

class DuplicationReporter:
    def __init__(self, source_root: Path):
        self.source_root = source_root

    def run(self) -> Dict[str, Any]:
        """
        Runs pylint duplication check.
        """
        pylint_cmd = shutil.which("pylint")
        if not pylint_cmd:
             # Fallback to current environment
             import sys
             candidate = Path(sys.executable).parent / "pylint"
             if candidate.exists():
                 pylint_cmd = str(candidate)

        if not pylint_cmd:
             logger.warning("Pylint executable not found. Skipping duplication check.")
             return {"status": "SKIPPED", "violation_count": 0, "details": "Pylint not installed"}

        # Run pylint with duplication check only
        # We use standard text output because parsing duplication from JSON can be complex
        cmd = [pylint_cmd, "--disable=all", "--enable=duplicate-code", str(self.source_root)]
        
        try:
            # Pylint returns non-zero if issues found
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            output = result.stdout
            
            # Parse output for "R0801: Similar lines in x files"
            # Format: R0801: Similar lines in 2 files
            # ==file1:[line:col]
            # ==file2:[line:col]
            
            duplicates = []
            
            lines = output.splitlines()
            current_dup = None
            
            for line in lines:
                if "R0801" in line:
                    if current_dup:
                        duplicates.append(current_dup)
                    current_dup = {"header": line, "files": []}
                elif current_dup and line.startswith("=="):
                     # Extract file path
                     match = re.search(r'==(.+):\[', line)
                     if match:
                         fpath = match.group(1).strip()
                         # Try to make relative
                         try:
                             rel_path = str(Path(fpath).relative_to(self.source_root))
                         except ValueError:
                             rel_path = fpath # Fallback
                         current_dup["files"].append(rel_path)
            
            if current_dup:
                duplicates.append(current_dup)
            
            violation_count = len(duplicates)
            status = "PASS" if violation_count == 0 else "FAIL"
            
            return {
                "status": status,
                "violation_count": violation_count,
                "details": duplicates,
                "raw_output": output
            }

        except Exception as e:
            logger.error(f"Failed to run pylint: {e}")
            return {"status": "ERROR", "violation_count": 0, "details": str(e)}
