from pathlib import Path
from typing import Dict, Any, List
import logging

try:
    import pandas as pd # type: ignore
    import seaborn as sns # type: ignore
    import matplotlib.pyplot as plt
    import numpy as np # type: ignore
except ImportError:
    pd = None
    sns = None
    plt = None
    np = None

from ..core.base_plotter import BasePlotter

class PerformancePlotter(BasePlotter):
    """Plotter for Performance and Timing Analysis."""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("nibandha.reporting.visualizers.performance")

    def plot(self, timings: List[Dict[str, Any]], output_dir: Path) -> Dict[str, str]:
        """Generate performance charts."""
        output_dir.mkdir(parents=True, exist_ok=True)
        charts = {}
        try:
            chart_path = output_dir / "performance_overall.png"
            self.plot_performance_distribution(timings, chart_path)
            if chart_path.exists(): charts["performance_overall"] = str(chart_path)
        except Exception as e:
            self.logger.error(f"Error generating performance charts: {e}")
        return charts

    def plot_performance_distribution(self, timings: List[Dict[str, Any]], output_path: Path) -> None:
        """Plot execution time breakdown (Total + 15 Stages)."""
        if not self._check_dependencies(): return
        self.setup_style()
        if not timings: return
            
        data = []
        for t in timings:
            try:
                val = float(str(t["duration"]).replace("s", ""))
                data.append({"Stage": t["stage"], "Duration (s)": val})
            except: continue
            
        if not data: return
        
        df = pd.DataFrame(data)
        df = df.sort_values("Duration (s)", ascending=False)
        
        # 1. Total Breakdown (Bar Plot)
        plt.figure(figsize=(12, 8))
        
        ax = sns.barplot(x="Duration (s)", y="Stage", data=df, palette="rocket", hue="Stage", legend=False)
        
        for container in ax.containers:
            ax.bar_label(container, fmt='%.3fs', padding=3)
            
        self._save_plot(output_path, "Report Generation Bottleneck Analysis")

        # 2. Deviation Analysis (Time vs Average)
        if not df.empty:
            avg_time = df["Duration (s)"].mean()
            
            plt.figure(figsize=(10, 6))
            
            df["Deviation"] = df["Duration (s)"] - avg_time
            df["Color"] = df["Deviation"].apply(lambda x: "#c0392b" if x > 0 else "#27ae60")
            
            sns.barplot(x="Deviation", y="Stage", data=df, palette=df["Color"].tolist(), hue="Stage", legend=False)
            plt.axvline(x=0, color='black', linestyle='--', linewidth=1)
            plt.xlabel(f"Seconds relative to Mean ({avg_time:.3f}s)")
                
            dev_path = output_path.parent / "performance_deviation.png"
            self._save_plot(dev_path, "Performance Deviation from Mean")
