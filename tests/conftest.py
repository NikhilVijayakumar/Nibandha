import pytest
from pathlib import Path
import tempfile
import shutil
import logging

# Force Matplotlib backend to Agg to prevent freezing
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from nibandha import Nibandha
from nibandha.configuration.domain.models.app_config import AppConfig
from nibandha.configuration.domain.models.rotation_config import LogRotationConfig


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


@pytest.fixture(autouse=True)
def cleanup_logger(sample_app_config):
    """Cleanup logger handlers after each test"""
    yield
    # Clean specific app logger
    loggers = [logging.getLogger(sample_app_config.name), logging.getLogger("nibandha"), logging.getLogger()]
    for logger in loggers:
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
            
    # Also clean manager to be safe
    logging.shutdown()
    import importlib
    importlib.reload(logging)
