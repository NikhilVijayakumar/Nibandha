import os
from pathlib import Path
from typing import Dict, Any, List
import logging

logger = logging.getLogger("nibandha.reporting.quality.encoding")

class EncodingReporter:
    """
    Scans project files to verify they are valid UTF-8.
    Also detects Byte Order Marks (BOM) which can cause issues in Linux environments.
    """
    
    def __init__(self, source_root: str):
        self.source_root = Path(source_root)
        self.extensions = {
            ".py", ".md", ".json", ".yaml", ".yml", 
            ".toml", ".txt", ".html", ".css", ".js", 
            ".xml", ".csv", ".ini", ".conf", ".sh"
        }
        
    def run(self) -> Dict[str, Any]:
        """
        Runs the encoding check.
        Returns:
            Dict containing status, violation count, and details.
        """
        logger.info(f"Running Encoding Check on {self.source_root}")
        
        violations = {
            "non_utf8": [],
            "bom_present": []
        }
        
        count = 0
        file_count = 0
        
        if not self.source_root.exists():
             return {
                "status": "ERROR",
                "violation_count": 0,
                "details": "Source root not found"
            }

        for root, dirs, files in os.walk(self.source_root):
            # Skip common ignores
            if "__pycache__" in root or ".venv" in root or ".git" in root or "build" in root or "dist" in root or ".idea" in root:
                continue
                
            for file in files:
                path = Path(root) / file
                if path.suffix.lower() not in self.extensions:
                    continue
                
                file_count += 1
                try:
                    rel_path = str(path.relative_to(self.source_root))
                except ValueError:
                    rel_path = str(path)

                # Check 1: Detect BOM
                try:
                    with open(path, 'rb') as f:
                        raw = f.read(4)
                    
                    if raw.startswith(b'\xef\xbb\xbf'):
                        violations["bom_present"].append({
                            "file": rel_path,
                            "error": "UTF-8 BOM detected"
                        })
                        count += 1
                        continue # If BOM exists, it is technically decodable as utf-8-sig but we flag it.
                        
                except Exception as e:
                    logger.warning(f"Failed to read file for BOM check: {path} - {e}")
                
                # Check 2: strict UTF-8 decoding
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        f.read()
                except UnicodeDecodeError as e:
                    violations["non_utf8"].append({
                        "file": rel_path,
                        "error": str(e)
                    })
                    count += 1
                except Exception as e:
                    # Permission error or other IO error
                    logger.warning(f"Failed to read file {path}: {e}")

        status = "PASS" if count == 0 else "FAIL"
        
        return {
            "status": status,
            "violation_count": count,
            "checked_count": file_count,
            "details": violations
        }
