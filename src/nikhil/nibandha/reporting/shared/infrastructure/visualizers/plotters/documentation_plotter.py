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

class DocumentationPlotter(BasePlotter):
    """Plotter for Documentation stats (Coverage & Drift)."""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("nibandha.reporting.visualizers.documentation")

    def plot(self, data: Dict[str, Any], output_dir: Path) -> Dict[str, str]:
        """Generate documentation charts."""
        output_dir.mkdir(parents=True, exist_ok=True)
        charts = {}
        try:
            total_doc = 0
            total_miss = 0
            for key in ["functional", "technical", "test"]:
                stats = data.get(key, {}).get("stats", {})
                total_doc += stats.get("documented", 0)
                total_miss += stats.get("missing", 0)
            cov_stats = {"Documented": total_doc, "Missing": total_miss}
            cov_path = output_dir / "doc_coverage.png"
            
            all_drifts = {}
            for key in ["functional", "technical", "test"]:
                dmap = data.get(key, {}).get("drift_map", {})
                for mod, days in dmap.items():
                    label = f"{mod} ({key[0].upper()})"
                    if days != -1: all_drifts[label] = days
            drift_path = output_dir / "doc_drift.png"
            
            self.plot_documentation_stats(cov_stats, all_drifts, cov_path, drift_path)
            
            if cov_path.exists(): charts["doc_coverage"] = str(cov_path)
            if drift_path.exists(): charts["doc_drift"] = str(drift_path)
        except Exception as e:
            self.logger.error(f"Error generating documentation charts: {e}")
        return charts

    def plot_documentation_stats(self, coverage_stats: Dict[str, int], drift_stats: Dict[str, int], output_path: Path, output_path_drift: Path) -> None:
        """Generate charts for documentation coverage and drift."""
        if not self._check_dependencies(): return
        self.setup_style()
        
        # 1. Coverage Donut
        if coverage_stats:
            labels = list(coverage_stats.keys())
            sizes = list(coverage_stats.values())
            if sum(sizes) > 0:
                plt.figure(figsize=(8, 8))
                colors = ["#2ecc71", "#e74c3c", "#95a5a6"] # Green, Red, Grey
                plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, pctdistance=0.85, explode=[0.02]*len(labels))
                
                centre_circle = plt.Circle((0,0), 0.70, fc='white')
                fig = plt.gcf()
                fig.gca().add_artist(centre_circle)
                
                self._save_plot(output_path, "Documentation Coverage Overview")

        # 2. Drift Histogram (Days)
        if drift_stats:
            df = pd.DataFrame(list(drift_stats.items()), columns=["Module", "DriftDays"])
            df = df.sort_values("DriftDays", ascending=False)
            
            plt.figure(figsize=(14, 8))
            
            colors = []
            for d in df["DriftDays"]:
                if d < 30: colors.append("#2ecc71")
                elif d < 90: colors.append("#f39c12")
                else: colors.append("#e74c3c")
                
            ax = sns.barplot(data=df, x="Module", y="DriftDays", palette=colors, hue="Module", legend=False)
            
            plt.ylabel("Days Since Last Doc Update")
            plt.xticks(rotation=45, ha="right")
            
            plt.axhline(y=30, color='#2ecc71', linestyle='--', label='Fresh (<30d)')
            plt.axhline(y=90, color='#e74c3c', linestyle='--', label='Stale (>90d)')
            plt.legend()
            
            self._save_plot(output_path_drift, "Documentation Drift Analysis")
