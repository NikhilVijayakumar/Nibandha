from pathlib import Path
from typing import Dict, Any
import logging

try:
    import pandas as pd # type: ignore
    import seaborn as sns # type: ignore
    import matplotlib.pyplot as plt
except ImportError:
    pd = None
    sns = None
    plt = None

from ..core.base_plotter import BasePlotter

class EncodingPlotter(BasePlotter):
    """Plotter for Encoding visualizations."""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("nibandha.reporting.visualizers.encoding")

    def plot(self, data: Dict[str, Any], output_dir: Path) -> Dict[str, str]:
        """Generate encoding charts."""
        output_dir.mkdir(parents=True, exist_ok=True)
        charts = {}
        try:
            status_counts = data.get("status_counts", {})
            if status_counts:
                status_path = output_dir / "encoding_status.png"
                self.plot_encoding_distribution(status_counts, status_path)
                if status_path.exists(): charts["encoding_status"] = str(status_path)
        except Exception as e:
            self.logger.error(f"Error generating encoding charts: {e}")
        return charts

    def plot_encoding_distribution(self, status_counts: Dict[str, int], output_path: Path) -> None:
        """Generate a pie chart for encoding status (UTF-8 vs Others)."""
        if not self._check_dependencies(): return
        self.setup_style()
        
        if not status_counts or sum(status_counts.values()) == 0: return

        labels = [k.replace("_", " ").title() for k in status_counts.keys()]
        sizes = list(status_counts.values())
        
        colors = []
        for k in status_counts.keys():
            k_lower = k.lower()
            if "utf-8" in k_lower or "utf8" in k_lower: colors.append("#2ecc71") # Green
            else: colors.append("#e74c3c") # Red

        plt.figure(figsize=(8, 8))
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, pctdistance=0.85, explode=[0.05]*len(labels) if len(labels)>1 else None)
        
        centre_circle = plt.Circle((0,0), 0.70, fc='white')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)
        
        self._save_plot(output_path, "File Encoding Distribution")
