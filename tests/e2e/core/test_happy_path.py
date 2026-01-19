
import pytest
import shutil
from pathlib import Path
from nibandha.core import Nibandha, AppConfig, LogRotationConfig

@pytest.fixture
def clean_env(tmp_path):
    """Provide a clean environment path."""
    yield tmp_path

def test_nibandha_full_lifecycle(clean_env):
    """
    E2E Happy Path: Initialize Nibandha -> Log -> Rotate -> Verify
    """
    # 1. Setup Config
    app_name = "E2E_Core_App"
    root_dir = clean_env / ".Nibandha"
    
    config = AppConfig(name=app_name, log_level="DEBUG")
    
    # 2. Initialize
    nb = Nibandha(config, root_name=str(root_dir))
    
    # Configure Rotation directly
    nb.rotation_config = LogRotationConfig(
        enabled=True,
        log_data_dir="logs/data",
        archive_dir="logs/archive",
        timestamp_format="%Y-%m-%d_%H-%M-%S"
    )
    
    nb.config_dir.mkdir(parents=True, exist_ok=True)
    import yaml
    with open(nb.config_dir / "rotation_config.yaml", "w") as f:
        yaml.dump(nb.rotation_config.model_dump(), f)
    
    # 3. Bind
    nb_bound = nb.bind()
    assert nb_bound.rotation_config.enabled is True
    
    # 4. Log Operations
    # Need to clean handlers created here, although fixtures in conftest usually handle units.
    # For E2E, we might need manual cleanup if 'cleanup_logger' fixture scopes to 'function' and matches name.
    # The app name here is "E2E_Core_App". Existing fixture mocks "sample_app_config" which is "TestApp".
    # So we should close handlers manually to avoid Windows issues.
    
    logger = nb_bound.logger
    logger.info("E2E Test Start")
    logger.error("Something went wrong (simulated)")
    
    # Flush
    for h in logger.handlers:
        h.flush()
        
    # 5. Verify Log File
    log_file = nb_bound.current_log_file
    assert log_file.exists()
    content = log_file.read_text()
    assert "E2E Test Start" in content
    
    # 6. Trigger Rotation
    # Core implementation handles necessary delays
    nb_bound.rotate_logs()
    
    # 7. Verify Archival
    archive_dir = nb_bound.app_root / "logs" / "archive"
    assert archive_dir.exists()
    archives = list(archive_dir.glob("*.log"))
    assert len(archives) == 1
    assert archives[0].name == log_file.name
    
    # Cleanup handlers explicitly for E2E
    for h in logger.handlers[:]:
        h.close()
        logger.removeHandler(h)
