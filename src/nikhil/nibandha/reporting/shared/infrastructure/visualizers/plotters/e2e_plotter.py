from pathlib import Path
from typing import Dict, Any, List
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

class E2EPlotter(BasePlotter):
    """Plotter for E2E Test visualizations."""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("nibandha.reporting.visualizers.e2e")

    def plot(self, data: Dict[str, Any], output_dir: Path) -> Dict[str, str]:
        """Generate all E2E charts and return their paths."""
        output_dir.mkdir(parents=True, exist_ok=True)
        charts = {}
        try:
            status_counts = data.get("status_counts", {})
            if status_counts:
                status_path = output_dir / "e2e_status.png"
                self.plot_e2e_outcome(status_counts, status_path)
                if status_path.exists(): charts["e2e_status"] = str(status_path)
            
            scenarios = data.get("scenarios", [])
            if scenarios:
                duration_path = output_dir / "e2e_durations.png"
                self.plot_e2e_durations(scenarios, duration_path)
                if duration_path.exists(): charts["e2e_durations"] = str(duration_path)
            
            modules = data.get("modules", [])
            mod_durations = {}
            for m in modules:
                mod_durations[m["name"]] = m.get("duration_val", 0.0)
            if mod_durations:
                mod_dur_path = output_dir / "e2e_module_durations.png"
                self.plot_module_durations(mod_durations, mod_dur_path)
                if mod_dur_path.exists(): charts["module_durations"] = str(mod_dur_path)
        except Exception as e:
            self.logger.error(f"Error generating E2E charts: {e}")
        return charts

    def plot_e2e_outcome(self, counts: Dict[str, int], output_path: Path) -> None:
        """Generate a donut chart for E2E outcomes."""
        if not self._check_dependencies(): return
        self.setup_style()
        
        labels = []
        sizes = []
        colors = []
        mapping = {"pass": "#2ecc71", "fail": "#e74c3c", "error": "#f1c40f", "skipped": "#95a5a6"}
        
        for k, v in counts.items():
            if v > 0:
                labels.append(k.title())
                sizes.append(v)
                colors.append(mapping.get(k, "#bdc3c7"))
                
        if not sizes: return

        plt.figure()
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, pctdistance=0.85, explode=[0.05]*len(sizes))
        
        centre_circle = plt.Circle((0,0), 0.70, fc='white')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)
        
        self._save_plot(output_path, "E2E Scenario Outcomes Overview")

    def plot_e2e_durations(self, scenarios: List[Dict[str, Any]], output_path: Path) -> None:
        """Horizontal Bar chart of duration per scenario."""
        if not self._check_dependencies(): return
        self.setup_style()
        
        df = pd.DataFrame(scenarios)
        if df.empty: return
        df = df.sort_values("duration", ascending=False)

        plt.figure(figsize=(12, max(6, len(df) * 0.4)))
        
        ax = sns.barplot(data=df, x="duration", y="name", hue="name", legend=False, palette="viridis")
        plt.xlabel("Time (s)")
        plt.ylabel("Scenario")
        
        for container in ax.containers:
            ax.bar_label(container, fmt='%.2fs', padding=3)

        self._save_plot(output_path, "E2E Scenario Performance Ranking")
        
    def plot_module_durations(self, module_durations: Dict[str, float], output_path: Path) -> None:
        """Generate a horizontal bar chart for module durations."""
        # This is shared with UnitPlotter, can be refactored to common if needed, or just duplicated
        if not self._check_dependencies(): return
        self.setup_style()
        
        if not module_durations: return
        
        df = pd.DataFrame(list(module_durations.items()), columns=["Module", "Duration"])
        df = df.sort_values("Duration", ascending=False)
        
        plt.figure(figsize=(12, 8))
        ax = sns.barplot(data=df, x="Duration", y="Module", hue="Module", legend=False, palette="magma")
        
        plt.xlabel("Execution Time (seconds)")
        plt.title("E2E Module Execution Performance Ranking", fontsize=16, fontweight='bold')
        
        for container in ax.containers:
            ax.bar_label(container, fmt='%.3fs', padding=3)
            
        self._save_plot(output_path, "E2E Module Execution Performance")
