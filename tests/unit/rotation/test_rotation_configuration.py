
import pytest
import yaml
import json
from pathlib import Path
from nibandha import Nibandha
from nibandha.configuration.domain.models.rotation_config import LogRotationConfig
from nibandha.logging.infrastructure.rotation_manager import RotationManager
import logging

class TestRotationConfiguration:
    """Test configuration loading from YAML/JSON files/CLI"""
    
    def test_load_cached_config_yaml(self, temp_root, sample_app_config):
        """Test loading existing YAML config"""
        config_dir = Path(temp_root) / ".Nibandha" / "config"
        config_dir.mkdir(parents=True)
        
        # Create YAML config
        config_file = config_dir / "rotation_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump({
                'enabled': True,
                'max_size_mb': 50,
                'rotation_interval_hours': 48,
                'archive_retention_days': 60
            }, f)
        
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        # _load_rotation_config is not exposed. Config is loaded during bind().
        # We can check nb.rotation_manager logic by calling bind().
        nb.bind()
        config = nb.rotation_config
        
        assert config is not None
        assert config.enabled is True
        assert config.max_size_mb == 50
        assert config.rotation_interval_hours == 48

    def test_save_rotation_config(self, temp_root, sample_app_config):
        """Test saving config to YAML file"""
        config_dir = Path(temp_root) / ".Nibandha" / "config"
        config_dir.mkdir(parents=True)
        
        nb = Nibandha(sample_app_config, root_name=str(Path(temp_root) / ".Nibandha"))
        rm = RotationManager(nb.config_dir, nb.app_root, logging.getLogger("test"))
        
        test_config = LogRotationConfig(enabled=True, max_size_mb=100)
        rm.save_config(test_config)
        
        config_file = config_dir / "rotation_config.yaml"
        assert config_file.exists()
        
        with open(config_file, 'r') as f:
            data = yaml.safe_load(f)
        assert data['enabled'] is True
        assert data['max_size_mb'] == 100
