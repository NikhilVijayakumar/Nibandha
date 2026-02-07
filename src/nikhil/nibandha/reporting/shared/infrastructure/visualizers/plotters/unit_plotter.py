from pathlib import Path
from typing import Dict, Any, List
import logging

try:
    import pandas as pd # type: ignore
    import seaborn as sns # type: ignore
    import matplotlib.pyplot as plt
    from nibandha.reporting.shared.domain.grading import GradingThresholds
except ImportError:
    pd = None
    sns = None
    plt = None
    GradingThresholds = None

from ..core.base_plotter import BasePlotter

class UnitPlotter(BasePlotter):
    """Plotter for Unit Test visualizations."""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("nibandha.reporting.visualizers.unit")

    def plot(self, data: Dict[str, Any], output_dir: Path) -> Dict[str, str]:
        """Generate all unit test charts and return their paths."""
        output_dir.mkdir(parents=True, exist_ok=True)
        charts = {}
        try:
            outcomes = data.get("outcomes_by_module", {})
            if outcomes:
                chart_path = output_dir / "unit_outcomes.png"
                self.plot_module_outcomes(outcomes, chart_path)
                if chart_path.exists(): charts["unit_outcomes"] = str(chart_path)
            
            coverage = data.get("coverage_by_module", {})
            if coverage:
                cov_path = output_dir / "unit_coverage.png"
                self.plot_coverage(coverage, cov_path)
                if cov_path.exists(): charts["unit_coverage"] = str(cov_path)
                    
            durations = data.get("durations", [])
            if durations:
                dur_path = output_dir / "unit_durations.png"
                self.plot_test_duration_distribution(durations, dur_path)
                if dur_path.exists(): charts["unit_durations"] = str(dur_path)
            
            modules = data.get("modules", [])
            mod_durations = {}
            for m in modules:
                mod_durations[m["name"]] = m.get("duration_val", 0.0)
            if mod_durations:
                mod_dur_path = output_dir / "unit_module_durations.png"
                self.plot_module_durations(mod_durations, mod_dur_path)
                if mod_dur_path.exists(): charts["module_durations"] = str(mod_dur_path)
            
            tests = data.get("tests", [])
            if tests:
                slow_path = output_dir / "unit_slowest_tests.png"
                self.plot_top_slowest_tests(tests, slow_path)
                if slow_path.exists(): charts["unit_slowest_tests"] = str(slow_path)
        except Exception as e:
            self.logger.error(f"Error generating unit charts: {e}")
        return charts

    def plot_module_outcomes(self, module_data: Dict[str, Any], output_path: Path) -> None:
        """Generate a stacked bar chart of Pass/Fail/Error counts per module."""
        if not self._check_dependencies(): return
        self.setup_style()
        
        data_list = []
        for mod, counts in module_data.items():
            total = counts.get("total", 0)
            if total == 0: continue
            data_list.append({"Module": mod, "Outcome": "Pass", "Count": counts.get("pass", 0)})
            data_list.append({"Module": mod, "Outcome": "Fail", "Count": counts.get("fail", 0)})
            data_list.append({"Module": mod, "Outcome": "Error", "Count": counts.get("error", 0)})
            
        df = pd.DataFrame(data_list)
        if df.empty: return

        try:
            df_pivot = df.pivot(index="Module", columns="Outcome", values="Count")
        except ValueError:
            return

        cols = [c for c in ["Pass", "Fail", "Error"] if c in df_pivot.columns]
        df_pivot = df_pivot[cols]
        
        df_pivot["Total"] = df_pivot.sum(axis=1)
        df_pivot["PassRate"] = (df_pivot.get("Pass", 0) / df_pivot["Total"]) * 100
        df_pivot = df_pivot.sort_values("Total", ascending=False)
        
        fig, ax1 = plt.subplots(figsize=(14, 8))
        
        colors = {"Pass": "#2ecc71", "Fail": "#e74c3c", "Error": "#f1c40f"}
        custom_palette = [colors[c] for c in cols]
        
        df_pivot[cols].plot(kind="bar", stacked=True, color=custom_palette, width=0.7, ax=ax1)
        ax1.set_ylabel("Test Count")
        ax1.set_xlabel("Module")
        ax1.legend(loc="upper left", title="Outcome")
        
        ax2 = ax1.twinx()
        sns.lineplot(data=df_pivot, x=df_pivot.index, y="PassRate", color="#2c3e50", marker="o", linewidth=2, ax=ax2, label="Pass Rate (%)")
        ax2.set_ylabel("Pass Rate (%)")
        ax2.set_ylim(0, 105)
        ax2.grid(False)
        
        for i, rate in enumerate(df_pivot["PassRate"]):
            if rate < 90:
                ax2.annotate(f"{rate:.1f}%", (i, rate), xytext=(0, -15), textcoords="offset points", ha='center', color="#c0392b", fontweight='bold')
        
        ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha="right")
        self._save_plot(output_path, "Module Test Outcomes & Pass Rate Analysis")

    def plot_coverage(self, module_data: Dict[str, float], output_path: Path) -> None:
        """Generate a bar chart for coverage percentage per module."""
        if not self._check_dependencies(): return
        self.setup_style()
        
        df = pd.DataFrame(list(module_data.items()), columns=["Module", "Coverage"])
        if df.empty: return
        df = df.sort_values("Coverage", ascending=True)

        plt.figure(figsize=(14, 8))
        
        colors = []
        for val in df["Coverage"]:
            if val < GradingThresholds.COVERAGE_CRITICAL: colors.append(GradingThresholds.COLOR_CRITICAL)
            elif val < GradingThresholds.COVERAGE_TARGET: colors.append(GradingThresholds.COLOR_WARNING)
            else: colors.append(GradingThresholds.COLOR_GOOD)
            
        ax = sns.barplot(data=df, x="Module", y="Coverage", palette=colors, hue="Module", legend=False)
        
        plt.axhline(y=GradingThresholds.COVERAGE_TARGET, color=GradingThresholds.COLOR_GOOD, linestyle='--', linewidth=2, label=f'Target ({GradingThresholds.COVERAGE_TARGET}%)')
        plt.axhline(y=GradingThresholds.COVERAGE_CRITICAL, color=GradingThresholds.COLOR_CRITICAL, linestyle='--', linewidth=2, label=f'Critical ({GradingThresholds.COVERAGE_CRITICAL}%)')
        plt.legend(loc="upper right")
        
        plt.ylabel("Coverage (%)")
        plt.ylim(0, 105)
        plt.xticks(rotation=45, ha="right")
        
        for i, v in enumerate(df["Coverage"]):
            ax.text(i, v + 1, f"{v:.1f}%", ha='center', fontsize=9, fontweight='bold')
            
        self._save_plot(output_path, "Code Coverage Risk Analysis")

    def plot_test_duration_distribution(self, test_durations: List[float], output_path: Path) -> None:
        """Generate a combined Histogram + KDE + Rug plot for duration analysis."""
        if not self._check_dependencies(): return
        self.setup_style()
        if not test_durations: return

        df = pd.DataFrame(test_durations, columns=["Duration"])
        
        plt.figure(figsize=(10, 6))
        sns.histplot(data=df, x="Duration", bins=40, kde=True, color="#3498db", line_kws={'linewidth': 2})
        sns.rugplot(data=df, x="Duration", color="#2c3e50", height=0.05)
        
        plt.xlabel("Duration (seconds)")
        plt.ylabel("Frequency")
        
        if df["Duration"].max() > 10 * df["Duration"].median() and df["Duration"].median() > 0:
            plt.xscale('log')
            plt.xlabel("Duration (seconds) - Log Scale")
            
        self._save_plot(output_path, "Test Duration Distribution Analysis")

    def plot_top_slowest_tests(self, tests: List[Dict[str, Any]], output_path: Path) -> None:
        """Generate a bar chart of the top 10 slowest tests."""
        if not self._check_dependencies(): return
        self.setup_style()
        if not tests: return
        
        valid_tests = []
        for t in tests:
            name = t.get("nodeid", "Unknown").split("::")[-1]
            dur = 0.0
            if "duration" in t and isinstance(t["duration"], (int, float)): dur = t["duration"]
            elif "call" in t: dur = t["call"].get("duration", 0)
            
            if "duration" in t and isinstance(t["duration"], str):
                 try: dur = float(t["duration"].replace("s", ""))
                 except: pass

            valid_tests.append({"Test": name, "Duration": dur})
            
        df = pd.DataFrame(valid_tests)
        if df.empty: return
        
        df = df.sort_values("Duration", ascending=False).head(10)
        
        plt.figure(figsize=(12, 8))
        ax = sns.barplot(data=df, x="Duration", y="Test", palette="magma", hue="Test", legend=False)
        
        plt.title("Top 10 Slowest Tests", fontsize=16, fontweight='bold')
        plt.xlabel("Duration (seconds)")
        
        for container in ax.containers:
            ax.bar_label(container, fmt='%.3fs', padding=3)
            
        self._save_plot(output_path, "Performance Bottlenecks: Top 10 Slowest Tests")

    def plot_module_durations(self, module_durations: Dict[str, float], output_path: Path) -> None:
        """Generate a horizontal bar chart for module durations."""
        if not self._check_dependencies(): return
        self.setup_style()
        
        if not module_durations: return
        
        df = pd.DataFrame(list(module_durations.items()), columns=["Module", "Duration"])
        df = df.sort_values("Duration", ascending=False)
        
        plt.figure(figsize=(12, 8))
        ax = sns.barplot(data=df, x="Duration", y="Module", hue="Module", legend=False, palette="magma")
        
        plt.xlabel("Execution Time (seconds)")
        plt.title("Module Execution Performance Ranking", fontsize=16, fontweight='bold')
        
        for container in ax.containers:
            ax.bar_label(container, fmt='%.3fs', padding=3)
            
        self._save_plot(output_path, "Module Execution Performance")
