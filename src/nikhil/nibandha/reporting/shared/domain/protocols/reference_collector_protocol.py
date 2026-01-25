"""
Protocol for reference collection services.

Defines the interface that reference collectors must implement to aggregate
figures, tables, and nomenclature from multiple report generators.
"""

from typing import Protocol
from ..reference_models import FigureReference, TableReference, NomenclatureItem, GlobalReferences


class ReferenceCollectorProtocol(Protocol):
    """
    Protocol defining the interface for collecting and aggregating report references.
    
    Implementations should provide thread-safe collection of references from multiple
    reporters and generate properly numbered global reference lists.
    """
    
    def add_figure(self, figure: FigureReference) -> None:
        """
        Register a figure reference.
        
        Args:
            figure: Figure metadata to add to the global collection
        """
        ...
    
    def add_table(self, table: TableReference) -> None:
        """
        Register a table reference.
        
        Args:
            table: Table metadata to add to the global collection
        """
        ...
    
    def add_nomenclature(self, item: NomenclatureItem) -> None:
        """
        Register a nomenclature/glossary item.
        
        If a term with the same name already exists, implementations should
        merge the source_reports lists to track all usage locations.
        
        Args:
            item: Nomenclature item to add or merge
        """
        ...
    
    def get_all_references(self) -> GlobalReferences:
        """
        Retrieve all collected references with assigned global numbers.
        
        This method should:
        - Assign sequential global_number values to figures and tables
        - Sort nomenclature alphabetically by term
        - Deduplicate any identical entries
        
        Returns:
            Complete GlobalReferences object ready for template rendering
        """
        ...
    
    def clear(self) -> None:
        """
        Clear all collected references.
        
        Use this to reset the collector between report generation runs.
        """
        ...
