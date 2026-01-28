
import pytest
from unittest.mock import MagicMock, patch, ANY
from pathlib import Path

# Import functions directly
from nibandha.reporting.shared.infrastructure.visualizers import matplotlib_impl

class TestMatplotlibFunctions:
    
    @pytest.fixture
    def mock_plt(self):
        with patch("nibandha.reporting.shared.infrastructure.visualizers.matplotlib_impl.plt") as mock:
            yield mock
            
    @pytest.fixture
    def mock_sns(self):
        with patch("nibandha.reporting.shared.infrastructure.visualizers.matplotlib_impl.sns") as mock:
            yield mock

    @pytest.fixture
    def mock_nx(self):
        with patch("nibandha.reporting.shared.infrastructure.visualizers.matplotlib_impl.nx") as mock:
            yield mock

    def test_unit_plots(self, mock_plt, mock_sns, tmp_path):
        """Verify unit test plotting functions."""
        # Fix: Provide Dict, as implementation iterates .items()
        module_data = {
            "A": {"pass": 10, "fail": 2, "error": 0, "stmts": 100, "covered": 80},
            "B": {"pass": 5, "fail": 5, "error": 1, "stmts": 50, "covered": 10},
        }
        
        # Test plot_module_outcomes
        matplotlib_impl.plot_module_outcomes(module_data, tmp_path / "outcomes.png")
        assert mock_plt.savefig.called
        
        # Test plot_coverage
        # Update: plot_coverage builds DF from module_data.items(), expecting values to be coverage floats?
        # Let's check implementation of plot_coverage again.
        # Line 80: df = pd.DataFrame(list(module_data.items()), columns=["Module", "Coverage"])
        # So module_data values MUST be scalars (coverage percentage).
        cov_data = {"A": 80.0, "B": 10.0}
        matplotlib_impl.plot_coverage(cov_data, tmp_path / "coverage.png")
        assert mock_plt.savefig.called
        
        # Test duration
        durations = [0.1, 0.5, 1.2]
        matplotlib_impl.plot_test_duration_distribution(durations, tmp_path / "dur.png")
        assert mock_plt.savefig.called

    def test_e2e_plots(self, mock_plt, tmp_path):
        """Verify E2E plots."""
        counts = {"pass": 5, "fail": 1}
        matplotlib_impl.plot_e2e_outcome(counts, tmp_path / "pie.png")
        assert mock_plt.savefig.called
        
        # Fix: Provide flat data with 'name' and 'duration' keys
        scenarios = [{"name": "scen1", "duration": 1.0}, {"name": "scen2", "duration": 0.5}]
        matplotlib_impl.plot_e2e_durations(scenarios, tmp_path / "bar.png")
        assert mock_plt.savefig.called

    def test_dependency_plots(self, mock_plt, mock_nx, mock_sns, tmp_path):
        """Verify dependency plots."""
        # Ensure HAS_NETWORKX is True? We can patch it or rely on try-import
        with patch("nibandha.reporting.shared.infrastructure.visualizers.matplotlib_impl.HAS_NETWORKX", True):
            deps = {"A": {"B"}, "B": set()}
            
            # Graph
            matplotlib_impl.plot_dependency_graph(deps, tmp_path / "graph.png")
            assert mock_nx.DiGraph.called or mock_plt.savefig.called
            
            # Matrix
            matplotlib_impl.plot_dependency_matrix(deps, tmp_path / "matrix.png")
            assert mock_sns.heatmap.called
            assert mock_plt.savefig.called

    def test_doc_plots(self, mock_plt, tmp_path):
        """Verify documentation plots."""
        cov_stats = {"Functional": 80, "Technical": 50, "Test": 20}
        drift_stats = {"ModA": 5, "ModB": 0}
        
        matplotlib_impl.plot_documentation_stats(
            cov_stats, drift_stats, 
            tmp_path / "doc_cov.png", 
            tmp_path / "doc_drift.png"
        )
        assert mock_plt.savefig.call_count >= 1 # Might save multiple or 2 calls
