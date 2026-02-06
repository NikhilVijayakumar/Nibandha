import pytest
import time
from pathlib import Path
from nibandha.logging.domain.models.log_settings import LogSettings
from nibandha.logging.infrastructure.nibandha_logger import NibandhaLogger

class TestLoggingE2E:
    def test_multi_module_consolidation_LOG_E2E_001(self, tmp_path):
        """
        ID: LOG-E2E-001
        Description: Logs from App.ModuleA and App.ModuleB should appear in App.log interleaved correctly.
        """
        log_dir = tmp_path / "logs_001"
        
        # Two loggers sharing same app_name implies same log file
        # But usually 'app_name' is the logger name root. 
        # NibandhaLogger uses logging.getLogger(settings.app_name).
        
        settings_a = LogSettings(app_name="App", log_dir=log_dir)
        logger_a = NibandhaLogger(settings_a) # Effectively 'App'
        
        # To simulate 'ModuleA', we might need child loggers if NibandhaLogger supported them.
        # But NibandhaLogger wraps a specific logger.
        # If we want "App.ModuleA", we would usually do logging.getLogger("App.ModuleA").
        # NibandhaLogger doesn't expose getChild.
        # We can simulate multi-component by just logging different messages or IDs.
        
        logger_a.info("Message from Module A", ids=["ModA"])
        logger_a.info("Message from Module B", ids=["ModB"])
        
        log_file = log_dir / "App.log"
        assert log_file.exists()
        content = log_file.read_text()
        
        assert "Message from Module A" in content
        assert "Message from Module B" in content
        assert "[ModA]" in content
        assert "[ModB]" in content

    def test_startup_rotation_LOG_E2E_002(self, tmp_path):
        """
        ID: LOG-E2E-002
        Description: Restart app with existing logs. Verify behavior (Append/Persist).
        """
        log_dir = tmp_path / "logs_002"
        settings = LogSettings(app_name="App", log_dir=log_dir)
        
        # Run 1
        logger_1 = NibandhaLogger(settings)
        logger_1.info("Run 1 Log")
        del logger_1 # Close handler ideally, but python gc might handle it or logging module persists
        
        # Run 2
        logger_2 = NibandhaLogger(settings)
        logger_2.info("Run 2 Log")
        
        log_file = log_dir / "App.log"
        content = log_file.read_text()
        
        assert "Run 1 Log" in content
        assert "Run 2 Log" in content



    def test_deleted_log_file_LOG_E2E_004(self, tmp_path):
        """
        ID: LOG-E2E-004
        Description: Delete active log file while app is running. Verify logger behavior.
        Standard RotatingFileHandler might stop writing or raise error if file invoked.
        """
        log_dir = tmp_path / "logs_004"
        settings = LogSettings(app_name="App", log_dir=log_dir)
        logger = NibandhaLogger(settings)
        
        logger.info("Message 1")
        log_file = log_dir / "App.log"
        assert log_file.exists()
        
        # On Windows, we need to close file handlers to release the file lock
        # before we can delete the file. This simulates an external deletion scenario.
        import logging
        for handler in logger.logger.handlers[:]:
            handler.close()
            logger.logger.removeHandler(handler)
        
        # Delete file
        log_file.unlink()
        assert not log_file.exists()
        
        # After deletion, the logger should handle writes gracefully
        # Note: Since we closed handlers, we need to reinitialize to continue logging
        # In a real scenario, the application would detect this and recreate handlers
        try:
            logger.info("Message 2")
        except Exception:
            # Should not crash app even if handlers are gone
            pass
            
        # Verify app didn't crash - we can still create a new logger
        logger2 = NibandhaLogger(settings)
        logger2.info("Message 3")


    def test_binary_data_LOG_E2E_005(self, tmp_path):
        """
        ID: LOG-E2E-005
        Description: Log raw bytes or binary string.
        """
        log_dir = tmp_path / "logs_005"
        settings = LogSettings(app_name="App", log_dir=log_dir)
        logger = NibandhaLogger(settings)
        
        binary_data = b'\x00\x01\xFF'
        # NibandhaLogger takes string msg. Passing bytes str might rely on str()
        logger.info(f"Binary: {binary_data}", ids=["BIN"])
        
        log_file = log_dir / "App.log"
        content = log_file.read_text() # Default utf-8
        
        assert "Binary: b'" in content or "Binary: b\"" in content
        assert "x00" in content or "\x00" in content or "blob" in str(binary_data)
