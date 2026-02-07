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

class QualityPlotter(BasePlotter):
    """Plotter for Quality metrics (Architecture, Type Safety, Complexity)."""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("nibandha.reporting.visualizers.quality")

    def plot_type_safety(self, data: Dict[str, Any], output_dir: Path) -> Dict[str, str]:
        """Generate type safety charts."""
        output_dir.mkdir(parents=True, exist_ok=True)
        charts = {}
        try:
            errors_by_module = data.get("errors_by_module", {})
            if errors_by_module:
                module_path = output_dir / "type_errors_by_module.png"
                self.plot_type_errors_by_module(errors_by_module, module_path)
                if module_path.exists(): charts["type_errors_by_module"] = str(module_path)
            
            categories = data.get("errors_by_category", {})
            if categories:
                cat_path = output_dir / "error_categories.png"
                self.plot_error_categories(categories, cat_path)
                if cat_path.exists(): charts["error_categories"] = str(cat_path)
        except Exception as e:
            self.logger.error(f"Error generating type safety charts: {e}")
        return charts

    def plot_complexity(self, data: Dict[str, Any], output_dir: Path) -> Dict[str, str]:
        """Generate complexity charts."""
        output_dir.mkdir(parents=True, exist_ok=True)
        charts = {}
        try:
            violations = data.get("violations_by_module", {})
            chart_path = output_dir / "complexity_distribution.png"
            self.plot_complexity_distribution(violations, chart_path)
            if chart_path.exists(): charts["complexity_distribution"] = str(chart_path)
                
            scores = data.get("complexity_scores", {})
            if scores:
                box_path = output_dir / "complexity_boxplot.png"
                self.plot_complexity_boxplot(scores, box_path)
                if box_path.exists(): charts["complexity_boxplot"] = str(box_path)
        except Exception as e:
            self.logger.error(f"Error generating complexity charts: {e}")
        return charts

    def plot_architecture(self, data: Dict[str, Any], output_dir: Path) -> Dict[str, str]:
        """Generate architecture status chart."""
        output_dir.mkdir(parents=True, exist_ok=True)
        charts = {}
        try:
            status = data.get("status", "UNKNOWN")
            chart_path = output_dir / "architecture_status.png"
            self.plot_architecture_status(status, chart_path)
            if chart_path.exists(): charts["architecture_status"] = str(chart_path)
        except Exception as e:
            self.logger.error(f"Error generating architecture charts: {e}")
        return charts

    def plot_architecture_status(self, status: str, output_path: Path) -> None:
        """Generate a simple status indicator for architecture."""
        if not self._check_dependencies(): return
        self.setup_style()
        
        plt.figure(figsize=(8, 6))
        if status == "PASS":
            color = "#2ecc71"
            icon = "✓"
            msg = "Architecture Compliant"
            sub = "All dependencies respect layers"
        else:
            color = "#e74c3c"
            icon = "✗"
            msg = "Architecture Violations"
            sub = "Dependency rules broken"
        
        plt.text(0.5, 0.6, icon, ha='center', va='center', fontsize=100, color=color, fontweight='bold')
        plt.text(0.5, 0.4, msg, ha='center', va='center', fontsize=18, color="#2c3e50", fontweight='bold')
        plt.text(0.5, 0.3, sub, ha='center', va='center', fontsize=12, color="#7f8c8d")
        
        plt.axis('off')
        self._save_plot(output_path, "Architecture Compliance Status")

    def plot_type_errors_by_module(self, module_errors: Dict[str, Any], output_path: Path) -> None:
        """Generate a bar chart showing type errors per module."""
        if not self._check_dependencies(): return
        self.setup_style()
        if not module_errors: return
        
        df = pd.DataFrame(list(module_errors.items()), columns=["Module", "Errors"])
        df = df.sort_values("Errors", ascending=False)
        
        plt.figure(figsize=(14, 8))
        colors = []
        for val in df["Errors"]:
            if val == 0: colors.append("#2ecc71")
            elif val < 20: colors.append("#f1c40f")
            else: colors.append("#c0392b") # Dark Red for high errors
        
        ax = sns.barplot(data=df, x="Module", y="Errors", palette=colors, hue="Module", legend=False)
        plt.ylabel("Number of Type Errors")
        plt.xticks(rotation=45, ha="right")
        
        for i, v in enumerate(df["Errors"]):
            ax.text(i, v + 0.5, str(v), ha='center', fontsize=9, fontweight='bold')
    
        self._save_plot(output_path, "Type Safety Violations by Module")

    def plot_error_categories(self, category_stats: Dict[str, int], output_path: Path) -> None:
        """Generate a horizontal bar chart of error categories."""
        if not self._check_dependencies(): return
        self.setup_style()
        if not category_stats: return
        
        sorted_cats = sorted(category_stats.items(), key=lambda x: x[1], reverse=True)
        
        # Top 15 categories to avoid clutter
        top_n = 15
        if len(sorted_cats) > top_n:
            top_cats = dict(sorted_cats[:top_n])
        else:
            top_cats = dict(sorted_cats)
        
        df = pd.DataFrame(list(top_cats.items()), columns=["Category", "Count"])
        
        plt.figure(figsize=(12, 8))
        sns.barplot(data=df, x="Count", y="Category", palette="mako", hue="Category", legend=False)
        
        self._save_plot(output_path, "Top Type Error Categories")

    def plot_complexity_distribution(self, complexity_violations: Dict[str, int], output_path: Path) -> None:
        """Generate visualization for complexity violations."""
        if not self._check_dependencies(): return
        self.setup_style()
        
        if not complexity_violations or sum(complexity_violations.values()) == 0:
            plt.figure()
            plt.text(0.5, 0.5, "✅ Clean Complexity\nAll functions < 10 Cyclomatic Complexity", 
                    ha='center', va='center', fontsize=16, color='#2ecc71', fontweight='bold')
            plt.axis('off')
            self._save_plot(output_path, "Cyclomatic Complexity Status")
            return
        
        df = pd.DataFrame(list(complexity_violations.items()), columns=["Module", "Violations"])
        df = df.sort_values("Violations", ascending=False)
    
        plt.figure(figsize=(14, 8))
        ax = sns.barplot(data=df, x="Module", y="Violations", palette="Reds_r", hue="Module", legend=False)
        
        plt.ylabel("Functions with Complexity > 10")
        plt.xticks(rotation=45, ha="right")
        
        for i, v in enumerate(df["Violations"]):
            if v > 0:
                ax.text(i, v + 0.1, str(int(v)), ha='center', fontsize=10, fontweight='bold')
                
        self._save_plot(output_path, "Complexity Hotspots (Cyclomatic > 10)")

    def plot_complexity_boxplot(self, complexity_data: Dict[str, List[int]], output_path: Path) -> None:
        """Generate a boxplot of cyclomatic complexity per module."""
        if not self._check_dependencies(): return
        self.setup_style()
        
        data_list = []
        for mod, scores in complexity_data.items():
            if not scores: continue
            for s in scores:
                data_list.append({"Module": mod, "Complexity": s})
                
        df = pd.DataFrame(data_list)
        if df.empty: return
        
        median_order = df.groupby("Module")["Complexity"].median().sort_values(ascending=False).index
        
        plt.figure(figsize=(14, 8))
        sns.boxplot(data=df, x="Module", y="Complexity", order=median_order, palette="coolwarm", hue="Module", legend=False)
        
        plt.axhline(y=10, color='#e74c3c', linestyle='--', linewidth=2, label='Threshold (10)')
        plt.legend(loc="upper right")
        
        plt.title("Cyclomatic Complexity Distribution per Module", fontsize=16, fontweight='bold')
        plt.ylabel("Cyclomatic Complexity")
        plt.xticks(rotation=45, ha="right")
        
        try:
            plt.yscale('log')
            plt.ylabel("Cyclomatic Complexity (Log Scale)")
        except: pass
        
        self._save_plot(output_path, "Module Complexity Distribution (Boxplot)")
