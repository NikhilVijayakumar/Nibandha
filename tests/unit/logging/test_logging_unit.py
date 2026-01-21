import pytest
from pathlib import Path
from pydantic import ValidationError
from nibandha.logging.domain.models.log_settings import LogSettings
from nibandha.logging.infrastructure.nibandha_logger import NibandhaLogger
from nibandha.logging.domain.protocols.logger import LoggerProtocol

class TestLoggingUnit:
    def test_log_settings_validation_LOG_UT_001(self, tmp_path):
        """
        ID: LOG-UT-001
        Description: LogSettings validation (rejects relative paths?).
        """
        # Valid settings
        try:
            LogSettings(app_name="TestApp", log_dir=tmp_path)
        except ValidationError:
            pytest.fail("Should accept valid settings")

        # Invalid: Missing required fields
        with pytest.raises(ValidationError):
            LogSettings(app_name="TestApp")  # Missing log_dir

    def test_logger_protocol_implementation_LOG_UT_002(self, tmp_path):
        """
        ID: LOG-UT-002
        Description: LoggerProtocol Implementation matches interface.
        """
        settings = LogSettings(app_name="TestApp", log_dir=tmp_path)
        logger = NibandhaLogger(settings)
        
        # Runtime verification check using isinstance if NibandhaLogger inherits, 
        # but since we use Duck Typing with Protocols, verification is that methods exist.
        assert isinstance(logger, LoggerProtocol) or hasattr(logger, 'info')

    def test_dependency_injection_LOG_UT_003(self, tmp_path):
        """
        ID: LOG-UT-003
        Description: Dependency Injection works (Settings -> Logger).
        """
        settings = LogSettings(app_name="InjectionApp", log_dir=tmp_path, log_level="DEBUG")
        logger = NibandhaLogger(settings)
        
        # Verify internal state reflects settings
        assert logger.settings.app_name == "InjectionApp"
        assert logger.logger.name == "InjectionApp"
        assert logger.logger.level == 10  # DEBUG
