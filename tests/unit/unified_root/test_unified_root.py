import pytest
from pathlib import Path
from nibandha.configuration.domain.models.app_config import AppConfig
from nibandha.unified_root.infrastructure.filesystem_binder import FileSystemBinder
from nibandha.unified_root.domain.models.root_context import RootContext

def test_root_context_immutability():
    ctx = RootContext(
        root=Path(".Test"),
        app_root=Path(".Test/App"),
        config_dir=Path(".Test/config"),
        log_base=Path(".Test/App"),
        report_dir=Path(".Test/App/Report")
    )
    from pydantic import ValidationError
    with pytest.raises((TypeError, ValidationError)):
        ctx.root = Path(".New")

def test_filsystem_binder_paths(tmp_path):
    # Setup
    root_name = tmp_path / ".NibandhaTest"
    config = AppConfig(name="TestApp", custom_folders=["data"])
    binder = FileSystemBinder()
    
    # Execute
    context = binder.bind(config, str(root_name))
    
    # Verify Context
    assert context.root == root_name
    assert context.app_root == root_name / "TestApp"
    assert context.config_dir == root_name / "config"
    
    # Verify File System
    assert context.app_root.exists()
    assert context.config_dir.exists()
    assert (context.app_root / "data").exists() # Custom folder
    assert (context.app_root / "logs").exists() # Legacy logs default
