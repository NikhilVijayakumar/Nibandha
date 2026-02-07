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

class SecurityPlotter(BasePlotter):
    """Plotter for Security visualizations."""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("nibandha.reporting.visualizers.security")

    def plot(self, data: Dict[str, Any], output_dir: Path) -> Dict[str, str]:
        """Generate security charts."""
        output_dir.mkdir(parents=True, exist_ok=True)
        charts = {}
        try:
            severity_counts = data.get("severity_counts", {})
            if severity_counts:
                sev_path = output_dir / "security_severity.png"
                self.plot_severity_distribution(severity_counts, sev_path)
                if sev_path.exists(): charts["security_severity"] = str(sev_path)
                
            module_counts = data.get("module_counts", {})
            if module_counts:
                hotspot_path = output_dir / "security_hotspots.png"
                self.plot_security_hotspots(module_counts, hotspot_path)
                if hotspot_path.exists(): charts["security_hotspots"] = str(hotspot_path)
        except Exception as e:
            self.logger.error(f"Error generating security charts: {e}")
        return charts

    def plot_severity_distribution(self, severity_counts: Dict[str, int], output_path: Path) -> None:
        """Generate a pie chart for security severity distribution."""
        if not self._check_dependencies(): return
        self.setup_style()
        
        if not severity_counts or sum(severity_counts.values()) == 0: return
        
        labels = [k.title() for k in severity_counts.keys()]
        sizes = list(severity_counts.values())
        
        colors = []
        for k in severity_counts.keys():
            k_lower = k.lower()
            if "high" in k_lower: colors.append("#c0392b") # Dark Red
            elif "medium" in k_lower: colors.append("#e67e22") # Orange
            elif "low" in k_lower: colors.append("#f1c40f") # Yellow
            else: colors.append("#95a5a6") # Grey

        plt.figure(figsize=(8, 8))
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, pctdistance=0.85, explode=[0.05]*len(labels))
        
        centre_circle = plt.Circle((0,0), 0.70, fc='white')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)
        
        self._save_plot(output_path, "Security Severity Distribution")

    def plot_security_hotspots(self, module_counts: Dict[str, int], output_path: Path) -> None:
        """Generate a bar chart of modules with the most security issues."""
        if not self._check_dependencies(): return
        self.setup_style()
        
        if not module_counts: return
        
        df = pd.DataFrame(list(module_counts.items()), columns=["Module", "Violations"])
        df = df[df["Violations"] > 0].sort_values("Violations", ascending=False).head(10)
        
        if df.empty: return
        
        plt.figure(figsize=(12, 8))
        ax = sns.barplot(data=df, x="Violations", y="Module", palette="Reds_r", hue="Module", legend=False)
        
        plt.title("Top 10 Security Hotspots", fontsize=16, fontweight='bold', pad=20)
        plt.xlabel("Total Issues")
        plt.ylabel("Module")
        
        for container in ax.containers:
            ax.bar_label(container, padding=5, fontweight='bold')
            
        self._save_plot(output_path, "Security Hotspots")
