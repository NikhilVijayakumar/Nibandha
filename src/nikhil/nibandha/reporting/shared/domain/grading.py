from typing import List, Dict, Any, Literal
from dataclasses import dataclass

Grade = Literal["A", "B", "C", "F"]

@dataclass(frozen=True)
class GradingThresholds:
    """Centralized thresholds for grading and visualization."""
    PASS_RATE_TARGET: float = 90.0  # Grade A/B cut-off
    PASS_RATE_CRITICAL: float = 75.0 # Grade F cut-off (below this is Fail)
    PASS_RATE_WARNING: float = 85.0 # Grade C cut-off (below this is C)
    
    COVERAGE_TARGET: float = 90.0   # Grade A (Excellent)
    COVERAGE_GOOD: float = 85.0     # Grade B
    COVERAGE_CRITICAL: float = 75.0 # Grade C/F cut-off
    
    # Visualization Colors (Hex)
    COLOR_GOOD: str = "#27ae60"    # Green
    COLOR_WARNING: str = "#f39c12" # Orange/Yellow
    COLOR_CRITICAL: str = "#c0392b" # Red

    # Quality Violations
    MAX_VIOLATIONS_A: int = 0
    MAX_VIOLATIONS_B: int = 3
    MAX_VIOLATIONS_C: int = 5
    
    # Dependency Health
    MAX_CIRCULAR_A: int = 0
    MAX_CIRCULAR_B: int = 1
    MAX_CIRCULAR_C: int = 2

class Grader:
    """Domain service for calculating report grades."""
    
    @staticmethod
    def calculate_unit_grade(pass_rate: float, coverage: float) -> Grade:
        """
        A: Pass Rate >= 90% AND Coverage >= 90%
        B: Pass Rate >= 85% AND Coverage >= 85%
        C: Pass Rate >= 75% AND Coverage >= 75%
        F: Failure to meet C criteria (< 75%)
        """
        if pass_rate >= GradingThresholds.PASS_RATE_TARGET and coverage >= GradingThresholds.COVERAGE_TARGET:
            return "A"
        if pass_rate >= GradingThresholds.PASS_RATE_WARNING and coverage >= GradingThresholds.COVERAGE_GOOD:
            return "B"
        if pass_rate >= GradingThresholds.PASS_RATE_CRITICAL and coverage >= GradingThresholds.COVERAGE_CRITICAL:
            return "C"
        return "F"

    @staticmethod
    def calculate_e2e_grade(pass_rate: float) -> Grade:
        """
        A: Pass Rate >= 90%
        B: Pass Rate >= 85%
        C: Pass Rate >= 75%
        F: Failure to meet C criteria (< 75%)
        """
        if pass_rate >= GradingThresholds.PASS_RATE_TARGET:
            return "A"
        if pass_rate >= GradingThresholds.PASS_RATE_WARNING:
            return "B"
        if pass_rate >= GradingThresholds.PASS_RATE_CRITICAL:
            return "C"
        return "F"
        
    @staticmethod
    def calculate_quality_grade(violations: int, is_fatal: bool = False) -> Grade:
        """
        A: 0 Violations and No Fatal Errors
        B: <= 3 Violations
        C: <= 5 Violations
        F: > 5 Violations OR Fatal Errors
        """
        if violations == 0 and not is_fatal:
            return "A"
        if is_fatal:
            return "F"
        if violations <= GradingThresholds.MAX_VIOLATIONS_B:
            return "B"
        if violations <= GradingThresholds.MAX_VIOLATIONS_C:
            return "C"
        return "F"
        
    @staticmethod
    def calculate_dependency_grade(circular_count: int) -> Grade:
        """
        A: 0 Circular Dependencies
        B: <= 1 Circular Dependencies
        C: <= 2 Circular Dependencies
        F: > 2 Circular Dependencies
        """
        if circular_count == GradingThresholds.MAX_CIRCULAR_A:
            return "A"
        if circular_count <= GradingThresholds.MAX_CIRCULAR_B:
            return "B"
        if circular_count <= GradingThresholds.MAX_CIRCULAR_C:
            return "C"
        return "F"

    @staticmethod
    def calculate_package_grade(health_score: int) -> Grade:
        """
        A: Health Score >= 90
        B: Health Score >= 85
        C: Health Score >= 75
        F: Health Score < 75
        """
        if health_score >= 90:
            return "A"
        if health_score >= 85:
            return "B"
        if health_score >= 75:
            return "C"
        return "F"
        
    @staticmethod
    def calculate_overall_grade(grades: List[Grade]) -> Grade:
        """
        Determined by the lowest grade present.
        """
        if not grades:
            return "F"
        
        if "F" in grades:
            return "F"
        if "C" in grades:
            return "C"
        if "B" in grades:
            return "B"
            
        return "A"

    @staticmethod
    def get_grade_color(grade: Grade) -> str:
        if grade == "A": return "#2ecc71" # Green
        if grade == "B": return "#3498db" # Blue
        if grade == "C": return "#f1c40f" # Yellow
        return "#e74c3c" # Red

