
import pytest
from pathlib import Path
from nibandha.unified_root.bootstrap import Nibandha
from nibandha.configuration.domain.models.app_config import AppConfig

def test_nibandha_bind_creates_structure_ROOT_E2E_001(tmp_path):
    """Verify Nibandha.bind checks/creates directory structure."""
    # We use a subfolder in tmp_path as the 'unified root' to prevent polluting real system
    root = tmp_path / ".NibandhaTest"
    
    config = AppConfig(name="TestApp", log_level="INFO")
    app = Nibandha(config, root_name=str(root))
    
    app.bind()
    
    assert root.exists()
    assert (root / "TestApp").exists()
    assert (root / "TestApp" / "logs").exists()
    
    # Check log file creation
    assert app.current_log_file.exists()

def test_nibandha_logging_setup_ROOT_E2E_002(tmp_path):
    """Verify logger writes to the bound file."""
    root = tmp_path / ".NibandhaLogTest"
    config = AppConfig(name="LoggerTest", log_level="INFO")
    app = Nibandha(config, root_name=str(root))
    app.bind()
    
    app.logger.info("Hello E2E World")
    
    content = app.current_log_file.read_text("utf-8")
    assert "Hello E2E World" in content
