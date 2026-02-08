"""Helper class for loading metrics cards from JSON files."""
import logging
import json
import re
from pathlib import Path
from typing import List, Dict, Any

from nibandha.configuration.domain.models.export_config import ExportConfig

logger = logging.getLogger("nibandha.export.helpers")


class MetricsCardLoader:
    """
    Loads metrics cards from JSON sidecar files.
    
    Uses configurable mapping to find JSON files corresponding to report files.
    """
    
    def __init__(self, config: ExportConfig):
        """
        Initialize with export configuration.
        
        Args:
            config: ExportConfig containing metrics_mapping
        """
        self.config = config
    
    def load_cards(self, detail_path: Path) -> List[Dict[str, Any]]:
        """
        Load metrics cards for a detail report.
        
        Constructs JSON path from detail markdown path using configured mapping.
        Expected structure:
        - detail_path: output_dir/details/unit_report.md
        - JSON path: output_dir/assets/data/unit.json
        
        Args:
            detail_path: Path to detail markdown file
            
        Returns:
            List of metrics card dictionaries, empty if not found or error
        """
        detail_stem = detail_path.stem
        
        # Strip numbering prefix if present (e.g., 03_unit_report -> unit_report)
        stripped_stem = re.sub(r'^\d+_', '', detail_stem)
        
        # Look up JSON name from mapping
        json_name = self.config.metrics_mapping.get(stripped_stem)
        
        if not json_name:
            logger.debug(f"No metrics mapping for report: {stripped_stem}")
            return []
        
        # Construct JSON path
        json_path = detail_path.parent.parent / "assets" / "data" / f"{json_name}.json"
        
        if not json_path.exists():
            logger.debug(f"Metrics JSON not found: {json_path}")
            return []
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                result: List[Dict[str, Any]] = data.get("metrics_cards", [])
                return result
        except Exception as e:
            logger.warning(f"Failed to load metrics cards from {json_path}: {e}")
            return []
