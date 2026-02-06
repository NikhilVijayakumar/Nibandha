"""
Domain models for global reference tracking.

This module provides Pydantic models for tracking figures, tables, and nomenclature
across all generated reports, enabling publication-standard reference sections.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List


class FigureReference(BaseModel):

    """
    Model representing a figure reference in the report collection.
    
    Attributes:
        id: Unique identifier for the figure (e.g., "fig-unit-1")
        title: Caption/title of the figure
        path: Relative path to the image file from the report root
        type: Type of visualization (e.g., "bar_chart", "histogram", "pie_chart")
        description: Detailed description of what the figure shows
        source_report: Name of the report this figure belongs to (e.g., "unit", "e2e")
        report_order: Order of the source report (1=unit, 2=e2e, 3=quality, etc.)
        module_number: Sequential number within the source report
        hierarchical_number: Publication-standard number (e.g., "1.1", "2.3")
        global_number: Sequential number assigned during aggregation (legacy, use hierarchical_number)
    """
    id: str
    title: str
    path: str
    type: str
    description: str
    source_report: str
    report_order: int = 0  # NEW: Report module number
    module_number: int = 0  # NEW: Sequential within report
    hierarchical_number: str = ""  # NEW: e.g., "1.1", "2.3"
    global_number: int = 0  # Legacy, kept for backward compatibility


class TableReference(BaseModel):
    """
    Model representing a table reference in the report collection.
    
    Attributes:
        id: Unique identifier for the table (e.g., "table-unit-1")
        title: Caption/title of the table
        description: Detailed description of the table contents
        source_report: Name of the report this table belongs to
        report_order: Order of the source report (1=unit, 2=e2e, etc.)
        module_number: Sequential number within the source report
        hierarchical_number: Publication-standard number (e.g., "1.1", "2.2")
        global_number: Sequential number assigned during aggregation (legacy)
    """
    id: str
    title: str
    description: str
    source_report: str
    report_order: int = 0  # NEW: Report module number
    module_number: int = 0  # NEW: Sequential within report
    hierarchical_number: str = ""  # NEW: e.g., "1.1", "2.2"
    global_number: int = 0  # Legacy


class NomenclatureItem(BaseModel):
    """
    Model representing a nomenclature/glossary term.
    
    Nomenclature items may appear in multiple reports, so we track which
    reports use each term to provide comprehensive cross-references.
    
    Attributes:
        term: The term or abbreviation being defined
        definition: Complete definition of the term
        source_reports: List of report names that use this term
    """
    term: str
    definition: str = Field(alias="def", default="")
    source_reports: List[str] = Field(default_factory=list)
    
    model_config = ConfigDict(populate_by_name=True)


class GlobalReferences(BaseModel):
    """
    Aggregated collection of all references from all reports.
    
    This model serves as the root data structure for the global reference
    document, containing deduplicated and properly numbered references.
    
    Attributes:
        figures: All figures from all reports, with assigned global numbers
        tables: All tables from all reports, with assigned global numbers
        nomenclature: All unique terms, alphabetically sorted with source tracking
    """
    figures: List[FigureReference] = Field(default_factory=list)
    tables: List[TableReference] = Field(default_factory=list)
    nomenclature: List[NomenclatureItem] = Field(default_factory=list)
