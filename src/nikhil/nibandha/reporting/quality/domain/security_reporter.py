import json
import shutil
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger("nibandha.reporting.quality.security")

class SecurityReporter:
    def __init__(self, source_root: Path):
        self.source_root = source_root

    def run(self) -> Dict[str, Any]:
        """
        Runs bandit security scan.
        """
        bandit_cmd = shutil.which("bandit")
        if not bandit_cmd:
             # Fallback to current environment
             import sys
             candidate = Path(sys.executable).parent / "bandit"
             if candidate.exists():
                 bandit_cmd = str(candidate)

        if not bandit_cmd:
             logger.warning("Bandit executable not found. Skipping security check.")
             return {"status": "SKIPPED", "violation_count": 0, "details": "Bandit not installed"}

        # Run bandit with JSON output
        cmd = [bandit_cmd, "-r", str(self.source_root), "-f", "json"]
        
        try:
            # Bandit returns exit code 1 if issues found, so we accept non-zero
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            output = result.stdout.strip()
            
            if not output:
                 logger.error("Bandit produced no output")
                 return {"status": "ERROR", "violation_count": 0, "details": f"No output. Stderr: {result.stderr}"}
                 
            try:
                # Find JSON start
                json_start = output.find('{')
                if json_start != -1:
                    output = output[json_start:]
                data = json.loads(output)
            except json.JSONDecodeError as e:
                # Fallback if mixed output
                 logger.error(f"Bandit output not JSON: {output[:100]}...")
                 return {"status": "ERROR", "violation_count": 0, "details": f"Invalid JSON: {str(e)}. Output start: {output[:50]}..."}

            results = data.get("results", [])
            
            # Filter for High/Medium severity
            high_severity = [r for r in results if r["issue_severity"] == "HIGH"]
            medium_severity = [r for r in results if r["issue_severity"] == "MEDIUM"]
            
            violation_count = len(high_severity) + len(medium_severity)
            status = "FAIL" if violation_count > 0 else "PASS"
            
            return {
                "status": status,
                "violation_count": violation_count,
                "details": {
                    "high": high_severity,
                    "medium": medium_severity,
                    "metrics": data.get("metrics", {})
                }
            }

        except Exception as e:
            logger.error(f"Failed to run bandit: {e}")
            return {"status": "ERROR", "violation_count": 0, "details": str(e)}
