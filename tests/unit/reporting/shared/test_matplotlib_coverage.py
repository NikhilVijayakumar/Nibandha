
import pytest
from unittest.mock import Mock, patch, MagicMock, ANY
from pathlib import Path
from nibandha.reporting.shared.infrastructure.visualizers import matplotlib_impl

# Create Mocks for external libs
mock_plt = MagicMock()
mock_sns = MagicMock()
mock_pd = MagicMock()
mock_nx = MagicMock()
mock_np = MagicMock()

@pytest.fixture
def mock_libs():
    with patch.multiple(matplotlib_impl, 
                        plt=mock_plt, 
                        sns=mock_sns, 
                        pd=mock_pd, 
                        nx=mock_nx,
                        np=mock_np,
                        HAS_NETWORKX=True):
        mock_plt.reset_mock()
        mock_sns.reset_mock()
        mock_pd.reset_mock()
        yield

def test_check_dependencies_missing():
    # Force None
    with patch.multiple(matplotlib_impl, plt=None, sns=None, pd=None):
        assert matplotlib_impl._check_dependencies() == False

def test_plot_module_outcomes(mock_libs, tmp_path):
    data = {"ModA": {"pass": 10, "fail": 0, "error": 0}}
    
    # Configure DataFrame Mock
    mock_df = MagicMock()
    mock_df.empty = False
    
    # Configure Pivot Result
    mock_pivot = MagicMock()
    mock_pivot.empty = False
    mock_pivot.columns = ["Pass", "Fail", "Error"] # Mock columns list
    
    # When subsetting pivot[cols], return a valid frame with empty=False
    mock_pivot.__getitem__.return_value.empty = False
    
    # Chain: DataFrame() -> returns mock_df -> pivot() -> returns mock_pivot
    mock_pd.DataFrame.return_value = mock_df
    mock_df.pivot.return_value = mock_pivot
    
    # Run
    matplotlib_impl.plot_module_outcomes(data, tmp_path / "out.png")
    
    # Verify
    mock_pd.DataFrame.assert_called()
    # plot is called on the subset (result of __getitem__), not the original pivot result
    mock_pivot.__getitem__.return_value.plot.assert_called() 
    mock_plt.savefig.assert_called()
    mock_plt.close.assert_called()

def test_plot_module_outcomes_empty(mock_libs, tmp_path):
    mock_df = MagicMock()
    mock_df.empty = True
    mock_pd.DataFrame.return_value = mock_df
    
    matplotlib_impl.plot_module_outcomes({}, tmp_path / "out.png")
    mock_plt.savefig.assert_not_called()

def test_plot_coverage(mock_libs, tmp_path):
    # Setup dataframe
    mock_df = MagicMock()
    mock_df.empty = False
    mock_pd.DataFrame.return_value = mock_df
    
    # Mock column access: df["Coverage"]
    # We need it to be iterable
    mock_col = MagicMock()
    mock_col.__iter__.return_value = [10.0, 60.0, 90.0]
    
    def getitem(key):
        if key == "Coverage": return mock_col
        return MagicMock()
        
    mock_df.__getitem__.side_effect = getitem
    
    data = {"A": 10.0, "B": 60.0, "C": 90.0}
    
    # Run
    matplotlib_impl.plot_coverage(data, tmp_path / "out.png")
    
    mock_sns.barplot.assert_called()
    
    # Verify palette
    args, kwargs = mock_sns.barplot.call_args
    assert "palette" in kwargs
    colors = kwargs["palette"]
    assert len(colors) == 3
    assert colors[0] == "#e74c3c" # < 50
    assert colors[1] == "#f1c40f" # < 80
    assert colors[2] == "#2ecc71" # > 80

def test_plot_dependency_graph(mock_libs, tmp_path):
    deps = {"A": ["B"], "B": ["C"]}
    matplotlib_impl.plot_dependency_graph(deps, tmp_path / "out.png")
    
    mock_nx.DiGraph.assert_called()
    mock_nx.draw_networkx_nodes.assert_called()
    mock_plt.savefig.assert_called()

def test_plot_dependency_graph_fallback(mock_libs, tmp_path):
    # Important: patch HAS_NETWORKX on the MODULE, not the mock fixture
    with patch("nibandha.reporting.shared.infrastructure.visualizers.matplotlib_impl.HAS_NETWORKX", False):
        matplotlib_impl.plot_dependency_graph({}, tmp_path / "out.png")
        # Should call _save_fallback_graph_image -> plt.savefig
        mock_plt.text.assert_called() 
        mock_plt.savefig.assert_called()

def test_plot_documentation_stats(mock_libs, tmp_path):
    # 1. Coverage
    cov = {"Functional": 100, "Technical": 50}
    drift = {"ModA": 10}
    
    matplotlib_impl.plot_documentation_stats(cov, drift, tmp_path / "cov.png", tmp_path / "drift.png")
    
    # Should save twice
    assert mock_plt.savefig.call_count >= 2
    mock_plt.pie.assert_called() # Coverage
    mock_sns.barplot.assert_called() # Drift

def test_plot_complexity(mock_libs, tmp_path):
    # Pass Case
    # Important: Need to ensure mock_plt is reset or checked carefully
    mock_plt.reset_mock()
    
    matplotlib_impl.plot_complexity_distribution({}, tmp_path / "out.png")
    
    # Use ANY for arguments we don't care about (fontsize, etc)
    # The message "[PASS] No Complexity Violations..."
    args, kwargs = mock_plt.text.call_args
    assert "[PASS]" in args[2] or "[PASS]" in kwargs.get("s", "")
    
    # Fail Case
    mock_plt.reset_mock()
    # Configure df for fail case
    mock_df = MagicMock()
    mock_col = MagicMock()
    mock_col.__iter__.return_value = [20]
    mock_df.__getitem__.return_value = mock_col
    mock_pd.DataFrame.return_value = mock_df
    
    matplotlib_impl.plot_complexity_distribution({"Mod": 20}, tmp_path / "out.png")
    mock_sns.barplot.assert_called()
