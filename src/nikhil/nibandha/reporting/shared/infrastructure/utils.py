import json
import shutil
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..domain.protocols.module_discovery import ModuleDiscoveryProtocol

# Use nibandha logger (assuming configured)
# For library utils, we might just print if logging isn't guaranteed, 
# but client requested "log than print". We'll try to get a logger.
import logging
logger = logging.getLogger("nibandha.reporting")

def load_json(path: Path) -> Dict[str, Any]:
    """Safe JSON load."""
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data: Dict[str, Any] = json.load(f)
            return data
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
    source_root: Optional[Path] = None,
    discovery: Optional["ModuleDiscoveryProtocol"] = None
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
    
    # Fallback to generic directory scanning of the source root
    try:
        root = source_root or Path.cwd() / "src"
        if not root.exists():
            return []
            
        modules = []
        for item in root.iterdir():
            if item.is_dir() and not item.name.startswith("__") and not item.name.startswith("."):
                modules.append(item.name.capitalize())
        return sorted(modules)
    except Exception as e:
        logger.error(f"Error finding modules: {e}")
        return []

def run_pytest(target: str, json_path: Path, cov_target: Optional[str] = None) -> bool:
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

def analyze_coverage(cov_data: dict, package_prefix: Optional[str] = None, known_modules: Optional[List[str]] = None) -> Tuple[Dict[str, float], float]:
    """Analyze coverage json."""
    if not cov_data:
        return {}, 0.0
        
    totals = cov_data.get("totals", {})
    files = cov_data.get("files", {})
    mod_stats = {} # mod: {hits: 0, lines: 0}
    
    if not package_prefix:
        package_prefix = "src/"

    for fpath, stats in files.items():
        fpath = fpath.replace("\\", "/")
        mod_name = _resolve_module_name(fpath, known_modules or [], package_prefix)
        
        if not mod_name: 
             logger.debug(f"Coverage mismatch for: {fpath} (Known: {known_modules})")
             continue

        if mod_name not in mod_stats:
             mod_stats[mod_name] = {"hits": 0, "lines": 0}
        
        summary = stats.get("summary", {})
        mod_stats[mod_name]["hits"] += summary.get("covered_lines", 0)
        mod_stats[mod_name]["lines"] += summary.get("num_statements", 0)
                
    return _calculate_coverage_results(mod_stats, totals)

def _resolve_module_name(fpath: str, known_modules: List[str], package_prefix: str) -> Optional[str]:
    """Resolve module name from file path using known modules or heuristics."""
    # 1. Try matching against known modules (Best Method)
    if known_modules:
        for mod in known_modules:
            if f"/{mod.lower()}/" in fpath.lower():
                return mod
    
    # 2. Fallback to path parsing
    rel_path = fpath
    if package_prefix in fpath:
         parts = fpath.split(package_prefix)
         if len(parts) > 1:
             rel_path = parts[1]
    elif "src/" in fpath:
         rel_path = fpath.split("src/")[1]
    
    parts = rel_path.split("/")
    if parts:
        mod_name = parts[0].capitalize()
        if mod_name.endswith(".py"):
             mod_name = mod_name.replace(".py", "").capitalize()
        return mod_name
        
    return None

def _calculate_coverage_results(mod_stats: Dict, totals: Dict) -> Tuple[Dict[str, float], float]:
    results = {}
    total_hits = 0
    total_lines = 0
    
    for mod, s in mod_stats.items():
        total_hits += s["hits"]
        total_lines += s["lines"]
        if s["lines"] > 0:
            results[mod] = (s["hits"] / s["lines"]) * 100
        else:
            results[mod] = 0.0
            
    if total_lines > 0:
        total_pct = (total_hits / total_lines) * 100
    else:
        total_pct = totals.get("percent_covered", 0.0)
            
    return results, total_pct

def save_report(path: Path, content: str) -> None:
    """Saves content to path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Report saved to: {path}")
    except Exception as e:
        logger.error(f"Error saving report to {path}: {e}")

def extract_module_name(file_path: str, source_root: Optional[Path] = None) -> str:
    """Extracts module name from a file path."""
    path = Path(file_path)
    
    # 1. Try from source root
    if source_root:
        name = _extract_from_source_root(path, source_root)
        if name: return name
            
    # 2. Try from src structure heuristics
    name = _extract_from_src_structure(path.parts)
    if name: return name

    # 3. Minimal fallback
    if len(path.parts) > 1:
        return path.parts[-2].capitalize()
    return "Unknown"

def _extract_from_source_root(path: Path, source_root: Path) -> Optional[str]:
    try:
        if path.is_absolute() and source_root.is_absolute():
             rel = path.relative_to(source_root)
             if len(rel.parts) > 0:
                  return rel.parts[0].capitalize()
    except (ValueError, Exception):
        pass
    return None

def _extract_from_src_structure(parts: Tuple[str, ...]) -> Optional[str]:
    if "src" in parts:
        try:
           idx = parts.index("src")
           # Check for nikhil/nibandha nesting
           if idx + 2 < len(parts) and parts[idx+1] == "nikhil" and parts[idx+2] == "nibandha":
               if idx + 3 < len(parts):
                   return parts[idx+3].capitalize()
           # Else generic src/module
           if idx + 1 < len(parts):
               return parts[idx+1].capitalize()
        except ValueError: 
             pass
    return None
