
import pytest
from pydantic import ValidationError
from nibandha.configuration.infrastructure.loaders import StandardConfigLoader
from nibandha.configuration.domain.models.app_config import AppConfig

def test_config_loader_happy_path_CFG_E2E_001():
    """Verify StandardConfigLoader creates a valid AppConfig."""
    loader = StandardConfigLoader(
        name="TestApp",
        log_level="DEBUG",
        custom_folders=["extra"]
    )
    config = loader.load()
    
    assert isinstance(config, AppConfig)
    assert config.name == "TestApp"
    assert config.log_level == "DEBUG"
    assert "extra" in config.custom_folders

def test_config_loader_defaults_CFG_E2E_002():
    """Verify defaults are applied."""
    loader = StandardConfigLoader(name="DefaultsApp")
    config = loader.load()
    
    assert config.log_level == "INFO"
    assert config.custom_folders == []

def test_config_validation_error_CFG_E2E_003():
    """Verify AppConfig validation (indirectly via Loader if possible, or direct)."""
    # Loader types are hinted but not enforced at runtime python-side unless pydantic validate arguments used.
    # AppConfig strictness depends on model.
    # Let's try to pass invalid list to custom_folders via kwargs/AppConfig directly if loader doesn't validate
    
    try:
        # Pydantic should catch string instead of list
        AppConfig(name="BadConfig", custom_folders="not-a-list", log_level="INFO")
        pytest.fail("Should have raised ValidationError")
    except ValidationError:
        pass
