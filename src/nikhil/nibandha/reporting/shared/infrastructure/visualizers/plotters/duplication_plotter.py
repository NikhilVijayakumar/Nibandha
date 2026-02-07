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

class DuplicationPlotter(BasePlotter):
    """Plotter for Duplication visualizations."""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("nibandha.reporting.visualizers.duplication")

    def plot(self, data: Dict[str, Any], output_dir: Path) -> Dict[str, str]:
        """Generate duplication charts."""
        output_dir.mkdir(parents=True, exist_ok=True)
        charts = {}
        try:
            module_counts = data.get("module_counts", {})
            if module_counts:
                hotspot_path = output_dir / "duplication_hotspots.png"
                self.plot_duplication_hotspots(module_counts, hotspot_path)
                if hotspot_path.exists(): charts["duplication_hotspots"] = str(hotspot_path)
        except Exception as e:
            self.logger.error(f"Error generating duplication charts: {e}")
        return charts

    def plot_duplication_hotspots(self, module_counts: Dict[str, int], output_path: Path) -> None:
        """Generate a bar chart of modules with the most duplicated lines/blocks."""
        if not self._check_dependencies(): return
        self.setup_style()
        
        if not module_counts: return
        
        df = pd.DataFrame(list(module_counts.items()), columns=["Module", "Duplicates"])
        df = df[df["Duplicates"] > 0].sort_values("Duplicates", ascending=False).head(15)
        
        if df.empty: return
        
        plt.figure(figsize=(14, 8))
        ax = sns.barplot(data=df, x="Duplicates", y="Module", palette="Oranges_r", hue="Module", legend=False)
        
        plt.title("Top 15 Duplication Hotspots", fontsize=16, fontweight='bold', pad=20)
        plt.xlabel("Duplicated Blocks")
        plt.ylabel("Module")
        
        for container in ax.containers:
            ax.bar_label(container, padding=5, fontweight='bold')
            
        self._save_plot(output_path, "Duplication Hotspots")
