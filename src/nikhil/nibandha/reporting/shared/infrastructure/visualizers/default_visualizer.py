from pathlib import Path
from typing import Dict, Any
import logging

# Import the low-level plotting library
# We reference the infra module where we moved matplotlib_impl
from ...infrastructure.visualizers import matplotlib_impl as visualizer

logger = logging.getLogger("nibandha.reporting")

class DefaultVisualizationProvider:
    """
    Default implementation of visualization generation.
    Uses the built-in matplotlib/seaborn visualizer module.
    """
    
    def generate_unit_test_charts(
        self, 
        data: Dict[str, Any], 
        output_dir: Path
    ) -> Dict[str, str]:
        """Generate unit test visualization charts."""
        output_dir.mkdir(parents=True, exist_ok=True)
        charts = {}
        
        try:
            # 1. Outcomes
            outcomes = data.get("outcomes_by_module", {})
            if outcomes:
                chart_path = output_dir / "unit_outcomes.png"
                visualizer.plot_module_outcomes(outcomes, chart_path)
                if chart_path.exists():
                    charts["unit_outcomes"] = str(chart_path)
            
            # 2. Coverage
            coverage = data.get("coverage_by_module", {})
            if coverage:
                cov_path = output_dir / "unit_coverage.png"
                visualizer.plot_coverage(coverage, cov_path)
                if cov_path.exists():
                    charts["unit_coverage"] = str(cov_path)
                    
            # 3. Durations
            durations = data.get("durations", [])
            if durations:
                dur_path = output_dir / "unit_durations.png"
                visualizer.plot_test_duration_distribution(durations, dur_path)
                if dur_path.exists():
                    charts["unit_durations"] = str(dur_path)

        except Exception as e:
            logger.error(f"Error generating unit charts: {e}")
            
        return charts
    
    def generate_e2e_test_charts(
        self, 
        data: Dict[str, Any], 
        output_dir: Path
    ) -> Dict[str, str]:
        """Generate E2E test charts."""
        output_dir.mkdir(parents=True, exist_ok=True)
        charts = {}
        
        try:
            # Status Pie Chart
            status_counts = data.get("status_counts", {})
            if status_counts:
                status_path = output_dir / "e2e_status.png"
                visualizer.plot_e2e_outcome(status_counts, status_path)
                if status_path.exists():
                    charts["e2e_status"] = str(status_path)
            
            # Duration Bar Chart
            scenarios = data.get("scenarios", [])
            if scenarios:
                duration_path = output_dir / "e2e_durations.png"
                visualizer.plot_e2e_durations(scenarios, duration_path)
                if duration_path.exists():
                    charts["e2e_durations"] = str(duration_path)
                    
        except Exception as e:
            logger.error(f"Error generating E2E charts: {e}")
            
        return charts
    
    def generate_type_safety_charts(
        self, 
        data: Dict[str, Any], 
        output_dir: Path
    ) -> Dict[str, str]:
        """Generate type safety charts."""
        output_dir.mkdir(parents=True, exist_ok=True)
        charts = {}
        
        try:
            # Errors by module
            errors_by_module = data.get("errors_by_module", {})
            if errors_by_module:
                module_path = output_dir / "type_errors_by_module.png"
                visualizer.plot_type_errors_by_module(errors_by_module, module_path)
                if module_path.exists():
                    charts["type_errors_by_module"] = str(module_path)
            
            # Error categories
            categories = data.get("errors_by_category", {})
            if categories:
                cat_path = output_dir / "error_categories.png"
                visualizer.plot_error_categories(categories, cat_path)
                if cat_path.exists():
                    charts["error_categories"] = str(cat_path)
                    
        except Exception as e:
            logger.error(f"Error generating type safety charts: {e}")
            
        return charts
    
    def generate_complexity_charts(
        self, 
        data: Dict[str, Any], 
        output_dir: Path
    ) -> Dict[str, str]:
        """Generate complexity charts."""
        output_dir.mkdir(parents=True, exist_ok=True)
        charts = {}
        
        try:
            violations = data.get("violations_by_module", {})
            chart_path = output_dir / "complexity_distribution.png"
            visualizer.plot_complexity_distribution(violations, chart_path)
            if chart_path.exists():
                charts["complexity_distribution"] = str(chart_path)
        except Exception as e:
            logger.error(f"Error generating complexity charts: {e}")
            
        return charts
    
    def generate_architecture_charts(
        self, 
        data: Dict[str, Any], 
        output_dir: Path
    ) -> Dict[str, str]:
        """Generate architecture charts."""
        output_dir.mkdir(parents=True, exist_ok=True)
        charts = {}
        
        try:
            status = data.get("status", "UNKNOWN")
            chart_path = output_dir / "architecture_status.png"
            visualizer.plot_architecture_status(status, chart_path)
            if chart_path.exists():
                charts["architecture_status"] = str(chart_path)
        except Exception as e:
            logger.error(f"Error generating architecture charts: {e}")
            
        return charts
