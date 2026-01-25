import json
import shutil
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from ..domain.protocols.module_discovery import ModuleDiscoveryProtocol

# Use nibandha logger (assuming configured)
# For library utils, we might just print if logging isn't guaranteed, 
# but client requested "log than print". We'll try to get a logger.
import logging
logger = logging.getLogger("nibandha.reporting")

def load_json(path: Path) -> dict:
    """Safe JSON load."""
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading {path}: {e}")
        return {}

def parse_outcome(data: dict) -> Tuple[int, int, int]:
    """Returns (passed, failed, total)."""
    summary = data.get("summary", {})
    passed = summary.get("passed", 0)
    failed = summary.get("failed", 0)
    total = passed + failed + summary.get("skipped", 0) + summary.get("error", 0)
    return passed, failed, total

def get_module_doc(docs_dir: Path, module_name: str, report_type: str = "unit") -> str:
    """Attempts to read documentation from the provided docs directory."""
    mod_lower = module_name.lower()
    doc_path = docs_dir / mod_lower / f"{report_type}_test_scenarios.md"
    
    if doc_path.exists():
        try:
            return doc_path.read_text(encoding="utf-8")
        except Exception:
            return "*Error reading documentation.*"
    return "*No documentation found for this module.*"

def get_all_modules(
    source_root: Path = None,
    discovery: "ModuleDiscoveryProtocol" = None
) -> List[str]:
    """
    Discover modules using provided protocol or default logic.
    
    Args:
        source_root: Optional root directory override (defaults to nibandha package root)
        discovery: Optional discovery protocol instance for custom module detection
        
    Returns:
        Sorted list of module names
        
    Example:
        >>> # Use default discovery for nibandha
        >>> modules = get_all_modules()
        >>> 
        >>> # Use custom discovery protocol
        >>> from ..infrastructure.standard_module_discovery import StandardModuleDiscovery
        >>> discovery = StandardModuleDiscovery()
        >>> modules = get_all_modules(Path("src/myproject"), discovery)
    """
    # If custom discovery is provided, use it
    if discovery:
        root = source_root or Path(__file__).parent.parent.parent.parent
        return discovery.discover_modules(root)
    
    # Fallback to default hardcoded behavior for backward compatibility
    try:
        # utils.py is in src/nikhil/nibandha/reporting/shared/infrastructure
        # nibandha is 4 parents up (nibandha/reporting/shared/infrastructure)
        nibandha_dir = source_root or Path(__file__).parent.parent.parent.parent
        modules = []
        for item in nibandha_dir.iterdir():
            if item.is_dir() and not item.name.startswith("__"):
                modules.append(item.name.capitalize())
        return sorted(modules)
    except Exception as e:
        logger.error(f"Error finding modules: {e}")
        return ["Core", "Logging", "Rotation"] # Fallback

def run_pytest(target: str, json_path: Path, cov_target: str = None) -> bool:
    """
    Run pytest and save to json_path.
    Returns True if execution finished (regardless of test failures), False on crash.
    """
    cmd = [
        sys.executable, "-m", "pytest",
        target,
        f"--json-report",
        f"--json-report-file={str(json_path)}",
    ]
    
    if cov_target:
        cmd.extend([
            f"--cov={cov_target}",
            "--cov-report=json",
            "--cov-report=term"
        ])

    logger.info(f"Running pytest on {target} -> {json_path}")
    try:
        # Popen to capture streaming output if needed, or just run
        # We use run for simplicity
        subprocess.run(cmd, check=False, env={**sys.modules['os'].environ})
        return True
    except Exception as e:
        logger.error(f"Error running pytest: {e}")
        return False

def analyze_coverage(cov_data: dict, package_prefix: str = "src/nikhil/nibandha/") -> Tuple[Dict[str, float], float]:
    """Analyze coverage json."""
    if not cov_data:
        return {}, 0.0
        
    totals = cov_data.get("totals", {})
    total_pct = totals.get("percent_covered", 0.0)
    
    files = cov_data.get("files", {})
    mod_stats = {} # mod: {hits: 0, lines: 0}
    
    for fpath, stats in files.items():
        # Normalize path separators
        fpath = fpath.replace("\\", "/")
        
        # Determine module name relative to the package prefix
        if package_prefix in fpath:
            parts = fpath.split(package_prefix)
            if len(parts) > 1:
                sub = parts[1] # e.g. auth/model/access_key.py
                mod_name = sub.split("/")[0].capitalize()
                
                if mod_name.endswith(".py"):
                    mod_name = mod_name.replace(".py", "").capitalize()
                
                if mod_name not in mod_stats:
                    mod_stats[mod_name] = {"hits": 0, "lines": 0}
                
                summary = stats.get("summary", {})
                mod_stats[mod_name]["hits"] += summary.get("covered_lines", 0)
                mod_stats[mod_name]["lines"] += summary.get("num_statements", 0)
                
    results = {}
    for mod, s in mod_stats.items():
        if s["lines"] > 0:
            results[mod] = (s["hits"] / s["lines"]) * 100
        else:
            results[mod] = 0.0
            
    return results, total_pct

def save_report(path: Path, content: str):
    """Saves content to path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Report saved to: {path}")
    except Exception as e:
        logger.error(f"Error saving report to {path}: {e}")
