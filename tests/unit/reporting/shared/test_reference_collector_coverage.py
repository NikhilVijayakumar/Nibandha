
import pytest
from nibandha.reporting.shared.application.reference_collector import ReferenceCollector
from nibandha.reporting.shared.domain.reference_models import (
    FigureReference, TableReference, NomenclatureItem
)

@pytest.fixture
def collector():
    return ReferenceCollector()

def test_add_figure_hierarchical_numbering(collector):
    # Report 1
    f1a = FigureReference(id="f1", title="F1", path="p1", type="img", description="d1", source_report="r1", report_order=1)
    f1b = FigureReference(id="f2", title="F2", path="p2", type="img", description="d2", source_report="r1", report_order=1)
    # Report 2
    f2a = FigureReference(id="f3", title="F3", path="p3", type="img", description="d3", source_report="r2", report_order=2)
    
    collector.add_figure(f1a)
    collector.add_figure(f1b)
    collector.add_figure(f2a)
    
    refs = collector.get_all_references()
    
    # Verify hierarchical numbering
    assert f1a.hierarchical_number == "1.1"
    assert f1a.module_number == 1
    
    assert f1b.hierarchical_number == "1.2"
    assert f1b.module_number == 2
    
    assert f2a.hierarchical_number == "2.1"
    assert f2a.module_number == 1
    
    # Original order preserved
    assert len(refs.figures) == 3

def test_add_table_hierarchical_numbering(collector):
    t1 = TableReference(id="t1", title="T1", description="d1", source_report="r1", report_order=1)
    t2 = TableReference(id="t2", title="T2", description="d2", source_report="r1", report_order=1)
    
    collector.add_table(t1)
    collector.add_table(t2)
    
    refs = collector.get_all_references()
    
    assert t1.hierarchical_number == "1.1"
    assert t2.hierarchical_number == "1.2"

def test_nomenclature_merge(collector):
    n1 = NomenclatureItem(term="API", definition="Interface", source_reports=["unit"])
    n2 = NomenclatureItem(term="api", definition="Interface", source_reports=["e2e"]) # Lowercase key match
    
    collector.add_nomenclature(n1)
    collector.add_nomenclature(n2)
    
    refs = collector.get_all_references()
    
    assert len(refs.nomenclature) == 1
    item = refs.nomenclature[0]
    assert item.term == "API" # Keeps first casing (or last? dictionary behavior, keeps first key usually)
    # Wait, implementation uses term.lower() as key.
    # But stores 'item' as value.
    # If key exists, it updates existing 'item'.
    assert "unit" in item.source_reports
    assert "e2e" in item.source_reports
    assert len(item.source_reports) == 2

def test_nomenclature_sorting(collector):
    n1 = NomenclatureItem(term="Zebra", definition="Z", source_reports=["r"])
    n2 = NomenclatureItem(term="Apple", definition="A", source_reports=["r"])
    
    collector.add_nomenclature(n1)
    collector.add_nomenclature(n2)
    
    refs = collector.get_all_references()
    
    assert refs.nomenclature[0].term == "Apple"
    assert refs.nomenclature[1].term == "Zebra"

def test_clear(collector):
    collector.add_figure(FigureReference(id="f", title="t", path="p", type="i", description="d", source_report="r", report_order=1))
    assert len(collector.get_all_references().figures) == 1
    
    collector.clear()
    assert len(collector.get_all_references().figures) == 0
