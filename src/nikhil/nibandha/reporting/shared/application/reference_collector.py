"""
Reference collector service implementation.

Provides centralized aggregation of figures, tables, and nomenclature from all
report generators, with automatic deduplication and hierarchical numbering.
"""

import logging
from typing import Dict, List
from nibandha.reporting.shared.domain.reference_models import (
    FigureReference,
    TableReference,
    NomenclatureItem,
    GlobalReferences
)

logger = logging.getLogger("nibandha.reporting.references")


class ReferenceCollector:
    """
    Centralized service for collecting and aggregating report references.
    
    This service collects figures, tables, and nomenclature items from all
    reporters and produces a unified, publication-standard reference document.
    
    Key features:
    - Automatic deduplication of nomenclature terms
    - Hierarchical numbering of figures and tables (1.1, 1.2, 2.1, 2.2, etc.)
    - Alphabetical sorting of nomenclature
    - Source tracking for cross-referencing
    """
    
    def __init__(self) -> None:
        """Initialize the reference collector with empty collections."""
        self._figures: List[FigureReference] = []
        self._tables: List[TableReference] = []
        self._nomenclature_dict: Dict[str, NomenclatureItem] = {}
        logger.debug("ReferenceCollector initialized")
    
    def add_figure(self, figure: FigureReference) -> None:
        """
        Add a figure reference to the collection.
        
        Args:
            figure: Figure metadata to register
        """
        self._figures.append(figure)
        logger.debug(f"Registered figure: {figure.id} from {figure.source_report}")
    
    def add_table(self, table: TableReference) -> None:
        """
        Add a table reference to the collection.
        
        Args:
            table: Table metadata to register
        """
        self._tables.append(table)
        logger.debug(f"Registered table: {table.id} from {table.source_report}")
    
    def add_nomenclature(self, item: NomenclatureItem) -> None:
        """
        Add or merge a nomenclature item.
        
        If a term with the same name already exists, this method merges the
        source_reports lists to track all reports that use the term.
        
        Args:
            item: Nomenclature item to add or merge
        """
        term_key = item.term.lower()  # Case-insensitive matching
        
        if term_key in self._nomenclature_dict:
            # Merge source reports
            existing = self._nomenclature_dict[term_key]
            existing.source_reports.extend(item.source_reports)
            existing.source_reports = sorted(list(set(existing.source_reports)))
            logger.debug(f"Merged nomenclature term '{item.term}' from {item.source_reports}")
        else:
            # Add new term
            self._nomenclature_dict[term_key] = item
            logger.debug(f"Registered nomenclature term '{item.term}' from {item.source_reports}")
    
    def get_all_references(self) -> GlobalReferences:
        """
        Retrieve all collected references with assigned hierarchical numbers.
        
        This method:
        1. Groups figures/tables by report_order
        2. Assigns module_number sequentially within each report  
        3. Generates hierarchical_number as "{report}.{module}" (e.g., "1.1", "2.3")
        4. Sorts nomenclature alphabetically by term
        5. Returns a complete GlobalReferences object
        
        Returns:
            GlobalReferences object ready for template rendering
        """
        # Group figures by report_order and assign hierarchical numbers
        figures_by_report: Dict[int, List[FigureReference]] = {}
        for fig in self._figures:
            if fig.report_order not in figures_by_report:
                figures_by_report[fig.report_order] = []
            figures_by_report[fig.report_order].append(fig)
        
        # Assign module numbers within each report
        for report_order in sorted(figures_by_report.keys()):
            for idx, fig in enumerate(figures_by_report[report_order], start=1):
                fig.module_number = idx
                fig.hierarchical_number = f"{report_order}.{idx}"
                fig.global_number = idx  # Also set for backward compat
        
        # Group tables by report_order and assign hierarchical numbers
        tables_by_report: Dict[int, List[TableReference]] = {}
        for tab in self._tables:
            if tab.report_order not in tables_by_report:
                tables_by_report[tab.report_order] = []
            tables_by_report[tab.report_order].append(tab)
        
        # Assign module numbers within each report
        for report_order in sorted(tables_by_report.keys()):
            for idx, tab in enumerate(tables_by_report[report_order], start=1):
                tab.module_number = idx
                tab.hierarchical_number = f"{report_order}.{idx}"
                tab.global_number = idx  # Also set for backward compat
        
        # Sort nomenclature alphabetically by term (case-insensitive)
        sorted_nomenclature = sorted(
            self._nomenclature_dict.values(),
            key=lambda x: x.term.lower()
        )
        
        logger.info(
            f"Generated global references with hierarchical numbering: "
            f"{len(self._figures)} figures, "
            f"{len(self._tables)} tables, "
            f"{len(sorted_nomenclature)} nomenclature items"
        )
        
        return GlobalReferences(
            figures=self._figures,
            tables=self._tables,
            nomenclature=sorted_nomenclature
        )
    
    def clear(self) -> None:
        """
        Clear all collected references.
        
        Use this to reset the collector between report generation runs.
        """
        self._figures.clear()
        self._tables.clear()
        self._nomenclature_dict.clear()
        logger.debug("ReferenceCollector cleared")
