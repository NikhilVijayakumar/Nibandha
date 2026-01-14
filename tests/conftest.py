import pytest
from pathlib import Path
import tempfile
import shutil
from nibandha.core import Nibandha, AppConfig, LogRotationConfig


@pytest.fixture
def temp_root():
    """Create a temporary directory for testing"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_app_config():
    """Sample app configuration"""
    return AppConfig(name="TestApp", custom_folders=["test_folder"])


@pytest.fixture
def rotation_config_enabled():
    """Enabled rotation config"""
    return LogRotationConfig(
        enabled=True,
        max_size_mb=1,  # 1MB for testing
        rotation_interval_hours=1,
        archive_retention_days=7
    )


@pytest.fixture
def rotation_config_disabled():
    """Disabled rotation config"""
    return LogRotationConfig(enabled=False)
