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

class ConclusionPlotter(BasePlotter):
    """Plotter for Conclusion/Scorecard visualizations."""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("nibandha.reporting.visualizers.conclusion")

    def plot(self, scores: Dict[str, Dict[str, str]], output_dir: Path) -> Dict[str, str]:
        """Generate conclusion charts."""
        output_dir.mkdir(parents=True, exist_ok=True)
        charts = {}
        try:
            scorecard_path = output_dir / "project_scorecard.png"
            self.plot_project_scorecard(scores, scorecard_path)
            if scorecard_path.exists(): charts["project_scorecard"] = str(scorecard_path)
        except Exception as e:
            self.logger.error(f"Error generating conclusion charts: {e}")
        return charts

    def plot_project_scorecard(self, scores: Dict[str, Dict[str, str]], output_path: Path) -> None:
        """
        Generate a summary scorecard image.
        scores format: {"Category": {"status": "PASS/FAIL", "grade": "A/B/C..."}}
        """
        if not self._check_dependencies(): return
        self.setup_style()
        
        if not scores: return
        
        # Prepare data for table
        categories = []
        statuses = []
        grades = []
        colors = []
        
        for cat, details in scores.items():
            categories.append(cat.replace("_", " ").title())
            status = details.get("status", "UNKNOWN")
            grade = details.get("grade", "-")
            
            statuses.append(status)
            grades.append(grade)
            
            if status == "PASS": colors.append("#2ecc71")
            elif status == "FAIL": colors.append("#e74c3c")
            else: colors.append("#95a5a6")
            
        # Create a figure acting as a table
        plt.figure(figsize=(10, len(categories) * 0.8 + 2))
        plt.axis('off')
        
        # Header
        plt.text(0.1, 0.95, "Category", weight='bold', size=14)
        plt.text(0.5, 0.95, "Status", weight='bold', size=14, ha='center')
        plt.text(0.8, 0.95, "Grade", weight='bold', size=14, ha='center')
        
        plt.plot([0.05, 0.95], [0.92, 0.92], color='black', linewidth=2)
        
        y = 0.85
        for i, cat in enumerate(categories):
            plt.text(0.1, y, cat, size=12, va='center')
            
            # Status badge (colored text for now, could be patch)
            status_text = statuses[i]
            status_color = colors[i]
            plt.text(0.5, y, status_text, size=12, weight='bold', color=status_color, ha='center', va='center')
            
            # Grade
            plt.text(0.8, y, grades[i], size=12, weight='bold', ha='center', va='center')
            
            # Divider
            plt.plot([0.05, 0.95], [y - 0.04, y - 0.04], color='#bdc3c7', linewidth=0.5, linestyle=':')
            
            y -= 0.08

        plt.title("Project Quality Scorecard", fontsize=18, fontweight='bold', pad=20)
        self._save_plot(output_path, "Project Scorecard", tight=False)
