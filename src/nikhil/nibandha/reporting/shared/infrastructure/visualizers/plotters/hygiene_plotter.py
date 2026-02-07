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

class HygienePlotter(BasePlotter):
    """Plotter for Code Hygiene visualizations."""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("nibandha.reporting.visualizers.hygiene")

    def plot(self, data: Dict[str, Any], output_dir: Path) -> Dict[str, str]:
        """Generate hygiene charts."""
        output_dir.mkdir(parents=True, exist_ok=True)
        charts = {}
        try:
            violation_counts = data.get("violation_counts", {})
            if violation_counts:
                status_path = output_dir / "hygiene_status.png"
                self.plot_hygiene_status(violation_counts, status_path)
                if status_path.exists(): charts["hygiene_status"] = str(status_path)
            
            module_counts = data.get("module_counts", {})
            if module_counts:
                hotspot_path = output_dir / "hygiene_hotspots.png"
                self.plot_hygiene_hotspots(module_counts, hotspot_path)
                if hotspot_path.exists(): charts["hygiene_hotspots"] = str(hotspot_path)
        except Exception as e:
            self.logger.error(f"Error generating hygiene charts: {e}")
        return charts

    def plot_hygiene_status(self, violation_counts: Dict[str, int], output_path: Path) -> None:
        """Generate a bar chart showing the breakdown of hygiene violation types."""
        if not self._check_dependencies(): return
        self.setup_style()
        
        if not violation_counts: return
        
        labels = {
            "magic_numbers": "Magic Numbers",
            "hardcoded_paths": "Hardcoded Paths",
            "forbidden_functions": "Forbidden Functions",
            "relative_imports": "Relative Imports"
        }
        
        data = []
        for k, v in violation_counts.items():
            data.append({"Violation Type": labels.get(k, k.replace("_", " ").title()), "Count": v})
            
        df = pd.DataFrame(data)
        df = df.sort_values("Count", ascending=False)
        
        plt.figure(figsize=(12, 8))
        
        colors = {
            "Magic Numbers": "#3498db",
            "Hardcoded Paths": "#e67e22",
            "Forbidden Functions": "#e74c3c", 
            "Relative Imports": "#9b59b6"
        }
        palette = [colors.get(x, "#95a5a6") for x in df["Violation Type"]]
        
        ax = sns.barplot(data=df, x="Count", y="Violation Type", palette=palette, hue="Violation Type", legend=False)
        
        plt.title("Code Hygiene Status: Violations by Type", fontsize=16, fontweight='bold', pad=20)
        plt.xlabel("Occurrences")
        plt.ylabel("")
        
        for container in ax.containers:
            ax.bar_label(container, padding=5, fontweight='bold')
            
        self._save_plot(output_path, "Code Hygiene Status")

    def plot_hygiene_hotspots(self, module_counts: Dict[str, int], output_path: Path) -> None:
        """Generate a horizontal bar chart identifying modules with most hygiene violations."""
        if not self._check_dependencies(): return
        self.setup_style()
        
        if not module_counts: return
        
        df = pd.DataFrame(list(module_counts.items()), columns=["Module", "Violations"])
        
        # Filter only modules with violations and take top 15
        df = df[df["Violations"] > 0].sort_values("Violations", ascending=False).head(15)
        
        if df.empty: return
        
        plt.figure(figsize=(14, 10))
        
        ax = sns.barplot(data=df, x="Violations", y="Module", palette="Reds_r", hue="Module", legend=False)
        
        plt.title("Top 15 Code Hygiene Hotspots (Most Violations)", fontsize=16, fontweight='bold', pad=20)
        plt.xlabel("Total Violations")
        plt.ylabel("Module")
        
        for container in ax.containers:
            ax.bar_label(container, padding=5, fontweight='bold')
            
        self._save_plot(output_path, "Hygiene Hotspots")
