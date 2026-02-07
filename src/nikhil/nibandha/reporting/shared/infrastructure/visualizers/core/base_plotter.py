import logging
from pathlib import Path
from typing import Optional, Dict, Any

# Optional dependencies
try:
    import seaborn as sns # type: ignore
    import matplotlib.pyplot as plt
    import pandas as pd # type: ignore
    import numpy as np
except ImportError:
    sns = None
    plt = None # type: ignore
    pd = None
    np = None # type: ignore

logger = logging.getLogger("nibandha.reporting.visualizers")

class BasePlotter:
    """Base class for all plotters containing shared logic."""
    
    def __init__(self):
        self.logger = logger

    def plot(self, data: 'Dict[str, Any]', output_dir: Path) -> 'Dict[str, str]':
        """
        Main execution method for generating charts.
        Should be implemented by subclasses.
        Returns a dictionary mapping chart names to their file paths.
        """
        return {}

    def _check_dependencies(self) -> bool:
        if not (sns and plt and pd):
            self.logger.warning("Visualization libraries (seaborn, matplotlib, pandas) not installed. Skipping plots.")
            return False
        return True

    def setup_style(self) -> None:
        """Set the aesthetic style of the plots."""
        if not self._check_dependencies(): return
        try:
            sns.set_theme(style="whitegrid", context="paper")
            plt.rcParams["figure.figsize"] = (12, 7)
            plt.rcParams["font.size"] = 12
            plt.rcParams["axes.titlesize"] = 14
            plt.rcParams["axes.labelsize"] = 12
            plt.rcParams["xtick.labelsize"] = 10
            plt.rcParams["ytick.labelsize"] = 10
            plt.rcParams["legend.fontsize"] = 10
            # Ensure we can render checkmarks and emojis on Windows/Mac/Linux
            plt.rcParams["font.sans-serif"] = ["Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", "DejaVu Sans", "Arial", "sans-serif"]
        except Exception as e:
            self.logger.warning(f"Failed to setup plot style: {e}")

    def _save_plot(self, output_path: Path, title: str, tight: bool = True) -> None:
        """Helper to save consistent plots."""
        if plt:
            try:
                plt.title(title, pad=20, fontsize=16, fontweight='bold')
                if tight:
                    plt.tight_layout()
                plt.savefig(output_path, dpi=150, bbox_inches='tight')
                self.logger.debug(f"Saved plot: {output_path}")
            except Exception as e:
                self.logger.error(f"Failed to save plot {output_path}: {e}")
            finally:
                plt.close()

    def _save_fallback_graph_image(self, output_path: Path, message: str = "Visualization unavailable") -> None:
        """Save a placeholder image when a specific library (like networkx) is missing."""
        if not plt: return
        try:
            plt.figure(figsize=(12, 8))
            plt.text(0.5, 0.5, message, ha='center', va='center', fontsize=14)
            plt.axis('off')
            plt.savefig(output_path)
            plt.close()
        except Exception as e:
            self.logger.error(f"Failed to save fallback image: {e}")
