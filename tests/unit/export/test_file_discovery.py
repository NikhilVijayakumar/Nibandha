"""Tests for FileDiscovery helper."""
import pytest
from pathlib import Path

from nibandha.configuration.domain.models.export_config import ExportConfig
from nibandha.export.application.helpers import FileDiscovery


class TestFileDiscovery:
    """Test file discovery, filtering, and ordering."""
    
    @pytest.fixture
    def sample_markdown_files(self, tmp_path):
        """Create sample markdown files for testing."""
        input_dir = tmp_path / "markdown"
        input_dir.mkdir()
        
        files = [
            "alpha.md",
            "beta.md",
            "gamma.md",
            "delta.md"
        ]
        
        for filename in files:
            (input_dir / filename).write_text(f"# {filename}")
        
        return input_dir
    
    def test_discover_files_alphabetic_default(self, sample_markdown_files, tmp_path):
        """Test default alphabetic ordering."""
        config = ExportConfig(
            input_dir=sample_markdown_files,
            output_dir=tmp_path / "output"
        )
        
        discovery = FileDiscovery(config)
        files = discovery.discover_files()
        
        assert len(files) == 4
        stems = [f.stem for f in files]
        assert stems == ["alpha", "beta", "delta", "gamma"]  # Alphabetic
    
    def test_discover_files_custom_order(self, sample_markdown_files, tmp_path):
        """Test custom export order."""
        config = ExportConfig(
            input_dir=sample_markdown_files,
            output_dir=tmp_path / "output",
            export_order=["gamma", "alpha", "beta"]  # Custom order, delta not specified
        )
        
        discovery = FileDiscovery(config)
        files = discovery.discover_files()
        
        assert len(files) == 4
        stems = [f.stem for f in files]
        # gamma, alpha, beta (ordered), then delta (unordered, alphabetic)
        assert stems == ["gamma", "alpha", "beta", "delta"]
    
    def test_discover_files_with_exclusions(self, sample_markdown_files, tmp_path):
        """Test file exclusions."""
        config = ExportConfig(
            input_dir=sample_markdown_files,
            output_dir=tmp_path / "output",
            exclude_files=["beta", "delta"]
        )
        
        discovery = FileDiscovery(config)
        files = discovery.discover_files()
        
        assert len(files) == 2
        stems = [f.stem for f in files]
        assert "beta" not in stems
        assert "delta" not in stems
        assert stems == ["alpha", "gamma"]
    
    def test_discover_files_with_order_and_exclusions(self, sample_markdown_files, tmp_path):
        """Test combining custom order with exclusions."""
        config = ExportConfig(
            input_dir=sample_markdown_files,
            output_dir=tmp_path / "output",
            export_order=["gamma", "beta", "alpha"],
            exclude_files=["beta"]  # beta excluded even though in order
        )
        
        discovery = FileDiscovery(config)
        files = discovery.discover_files()
        
        assert len(files) == 3
        stems = [f.stem for f in files]
        assert "beta" not in stems
        assert stems == ["gamma", "alpha", "delta"]
    
    def test_discover_files_missing_input_dir(self, tmp_path):
        """Test error when input_dir not configured."""
        config = ExportConfig(
            output_dir=tmp_path / "output"
            # No input_dir
        )
        
        discovery = FileDiscovery(config)
        
        with pytest.raises(ValueError, match="input_dir must be configured"):
            discovery.discover_files()
    
    def test_discover_files_nonexistent_input_dir(self, tmp_path):
        """Test error when input_dir doesn't exist."""
        config = ExportConfig(
            input_dir=tmp_path / "nonexistent",
            output_dir=tmp_path / "output"
        )
        
        discovery = FileDiscovery(config)
        
        with pytest.raises(ValueError, match="input_dir does not exist"):
            discovery.discover_files()
    
    def test_discover_files_empty_directory(self, tmp_path):
        """Test empty directory returns empty list."""
        input_dir = tmp_path / "empty"
        input_dir.mkdir()
        
        config = ExportConfig(
            input_dir=input_dir,
            output_dir=tmp_path / "output"
        )
        
        discovery = FileDiscovery(config)
        files = discovery.discover_files()
        
        assert files == []
