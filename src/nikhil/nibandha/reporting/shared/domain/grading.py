from typing import List, Dict, Any, Literal

Grade = Literal["A", "B", "F"]

class Grader:
    """Domain service for calculating report grades."""
    
    @staticmethod
    def calculate_unit_grade(pass_rate: float, coverage: float) -> Grade:
        """
        A: Pass Rate >= 95% AND Coverage >= 80%
        B: Pass Rate >= 80% AND Coverage >= 50%
        F: Failure to meet B criteria
        """
        if pass_rate >= 95 and coverage >= 80:
            return "A"
        if pass_rate >= 80 and coverage >= 50:
            return "B"
        return "F"

    @staticmethod
    def calculate_e2e_grade(pass_rate: float) -> Grade:
        """
        A: Pass Rate >= 95%
        B: Pass Rate >= 80%
        F: Failure to meet B criteria
        """
        if pass_rate >= 95:
            return "A"
        if pass_rate >= 80:
            return "B"
        return "F"
        
    @staticmethod
    def calculate_quality_grade(violations: int, is_fatal: bool = False) -> Grade:
        """
        A: 0 Violations and No Fatal Errors
        B: <= 5 Violations and No Fatal Errors
        F: > 5 Violations OR Fatal Errors
        """
        if is_fatal:
            return "F"
        if violations == 0:
            return "A"
        if violations <= 5:
            return "B"
        return "F"
        
    @staticmethod
    def calculate_dependency_grade(circular_count: int) -> Grade:
        """
        A: 0 Circular Dependencies
        B: <= 2 Circular Dependencies
        F: > 2 Circular Dependencies
        """
        if circular_count == 0:
            return "A"
        if circular_count <= 2:
            return "B"
        return "F"
        
    @staticmethod
    def calculate_overall_grade(grades: List[Grade]) -> Grade:
        """
        A: All grades must be A
        B: All grades must be A or B (no F)
        F: Any F results in overall F
        """
        if not grades:
            return "F"
        
        if "F" in grades:
            return "F"
            
        if all(g == "A" for g in grades):
            return "A"
            
        return "B"

    @staticmethod
    def get_grade_color(grade: Grade) -> str:
        if grade == "A": return "#2ecc71" # Green
        if grade == "B": return "#f1c40f" # Yellow
        return "#e74c3c" # Red
