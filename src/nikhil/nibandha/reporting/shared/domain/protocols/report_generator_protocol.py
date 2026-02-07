from typing import Protocol, Dict, Any, Optional

class ReportGeneratorProtocol(Protocol):
    """Protocol for all report generators."""
    
    def generate(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Generates a report.
        
        Args:
            **kwargs: Context-specific arguments required for generation.
            
        Returns:
            Dictionary containing report data/metrics.
        """
        ...
