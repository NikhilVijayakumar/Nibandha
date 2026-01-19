from typing import Protocol, Dict, Any, List
from pathlib import Path

class VisualizationProvider(Protocol):
    """Protocol for generating report visualizations.
    
    Clients can implement this protocol to provide custom visualizations.
    Each method should generate relevant charts and return a dictionary 
    mapping chart names (keys used in templates) to absolute file paths.
    """
    
    def generate_unit_test_charts(
        self, 
        data: Dict[str, Any], 
        output_dir: Path
    ) -> Dict[str, str]:
        """
        Generate unit test visualization charts.
        
        Args:
            data: Unit test data dictionary
            output_dir: Directory to save chart images
            
        Returns:
            Dictionary mapping chart names to file paths
        """
        ...
    
    def generate_e2e_test_charts(
        self, 
        data: Dict[str, Any], 
        output_dir: Path
    ) -> Dict[str, str]:
        """Generate E2E test charts."""
        ...
    
    def generate_type_safety_charts(
        self, 
        data: Dict[str, Any], 
        output_dir: Path
    ) -> Dict[str, str]:
        """Generate type safety charts."""
        ...
    
    def generate_complexity_charts(
        self, 
        data: Dict[str, Any], 
        output_dir: Path
    ) -> Dict[str, str]:
        """Generate complexity charts."""
        ...
    
    def generate_architecture_charts(
        self, 
        data: Dict[str, Any], 
        output_dir: Path
    ) -> Dict[str, str]:
        """Generate architecture charts."""
        ...
