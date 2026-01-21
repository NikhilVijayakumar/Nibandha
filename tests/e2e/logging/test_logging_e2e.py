import pytest
from pathlib import Path
from nibandha.logging.domain.models.log_settings import LogSettings
from nibandha.logging.infrastructure.nibandha_logger import NibandhaLogger

class TestLoggingE2E:
    def test_file_output_LOG_E2E_001(self, tmp_path):
        """
        ID: LOG-E2E-001
        Description: Write a log, read the file, verify format.
        """
        settings = LogSettings(app_name="E2E_App", log_dir=tmp_path)
        logger = NibandhaLogger(settings)
        
        logger.info("Hello E2E", ids=["ID-123"])
        
        log_file = tmp_path / "E2E_App.log"
        assert log_file.exists()
        
        content = log_file.read_text()
        assert "Hello E2E" in content
        assert "[ID-123]" in content
        assert "| INFO | [E2E_App] |" in content

    def test_multiple_instances_LOG_E2E_002(self, tmp_path):
        """
        ID: LOG-E2E-002
        Description: Verify multiple instances with different app_names write to separate files.
        """
        settings_a = LogSettings(app_name="App_A", log_dir=tmp_path)
        logger_a = NibandhaLogger(settings_a)
        
        settings_b = LogSettings(app_name="App_B", log_dir=tmp_path)
        logger_b = NibandhaLogger(settings_b)
        
        logger_a.info("Message A")
        logger_b.info("Message B")
        
        file_a = tmp_path / "App_A.log"
        file_b = tmp_path / "App_B.log"
        
        assert file_a.exists()
        assert file_b.exists()
        
        assert "Message A" in file_a.read_text()
        assert "Message B" not in file_a.read_text()
        
        assert "Message B" in file_b.read_text()
        assert "Message A" not in file_b.read_text()
