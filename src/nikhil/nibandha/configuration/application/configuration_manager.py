from pathlib import Path
from typing import Union, Dict, Any
import json
import yaml
from pydantic import ValidationError

from nibandha.configuration.domain.models.app_config import AppConfig

class ConfigurationManager:
    """
    Manages loading and validation of Application Configuration.
    Provides smart defaults - modules receive fully configured objects.
    """
    
    @staticmethod
    def load_from_dict(data: Dict[str, Any]) -> AppConfig:
        """
        Load configuration from a dictionary.
        Uses RobustConfigValidator for validation and sanitization.
        Falls back to default configuration on critical errors.
        
        Args:
            data: Configuration dictionary (can be partial).
            
        Returns:
            AppConfig: Validated application configuration with defaults.
        """
        try:
            # Validate and sanitize robustly
            from nibandha.configuration.infrastructure.robust_validator import RobustConfigValidator
            validator = RobustConfigValidator()
            clean_data = validator.validate_and_sanitize(AppConfig, data or {})
            
            # Log audit trail (info/debug level)
            import logging
            logger = logging.getLogger(__name__)
            for log_entry in validator.audit_log:
                 # logger.info(log_entry)
                 pass
                 
            return AppConfig(**clean_data)
            
        except (ValidationError, ValueError, TypeError) as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"❌ Configuration Validation Failed: {type(e).__name__}: {str(e)}")
            logger.warning("⚠️  Application starting with DEFAULT configuration due to validation failure.")
            # detailed observability
            print(f"ERROR: Config Validation: {e}")
            
            return ConfigurationManager.create_default()

    @staticmethod
    def load_from_json(path: Union[str, Path]) -> AppConfig:
        """
        Load configuration from a JSON file.
        
        Args:
            path: Path to JSON file.
            
        Returns:
            AppConfig: Validated application configuration.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")
            
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        return ConfigurationManager.load_from_dict(data)

    @staticmethod
    def load_from_yaml(path: Union[str, Path]) -> AppConfig:
        """
        Load configuration from a YAML file.
        
        Args:
            path: Path to YAML file.
            
        Returns:
            AppConfig: Validated application configuration.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")
            
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            
        return ConfigurationManager.load_from_dict(data)

    @staticmethod
    def create_default(app_name: str = None) -> AppConfig:
        """
        Create a default configuration.
        
        Args:
            app_name: Optional app name override.
            
        Returns:
            AppConfig with all defaults.
        """
        if app_name:
            return AppConfig(name=app_name)
        return AppConfig()
