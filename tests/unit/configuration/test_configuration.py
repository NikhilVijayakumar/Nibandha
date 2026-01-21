import pytest
from nibandha.configuration.domain.models.app_config import AppConfig
from nibandha.configuration.infrastructure.loaders import StandardConfigLoader

def test_app_config_creation():
    config = AppConfig(name="TestApp", log_level="DEBUG")
    assert config.name == "TestApp"
    assert config.log_level == "DEBUG"
    assert config.custom_folders == []

def test_standard_loader():
    loader = StandardConfigLoader(
        name="LoaderApp",
        custom_folders=["data"],
        log_dir="/tmp/logs"
    )
    config = loader.load()
    
    assert isinstance(config, AppConfig)
    assert config.name == "LoaderApp"
    assert "data" in config.custom_folders
    assert config.log_dir == "/tmp/logs"
