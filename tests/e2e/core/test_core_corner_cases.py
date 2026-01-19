
import pytest
from pathlib import Path
from nibandha.core import Nibandha, AppConfig

@pytest.fixture
def clean_env(tmp_path):
    yield tmp_path

def test_bind_twice(clean_env):
    """E2E Corner: Binding twice shouldn't crash but might effectively re-init logs."""
    app_name = "E2E_Twice"
    root_dir = clean_env / ".Nibandha"
    config = AppConfig(name=app_name)
    
    nb = Nibandha(config, root_name=str(root_dir))
    nb.bind()
    
    nb.logger.info("First bind")
    
    # Re-bind? Usually one instance is used.
    # Calling bind again on same instance:
    nb.bind()
    nb.logger.info("Second bind")
    
    # Should have handlers attached still (maybe doubled if not careful?)
    # Nibandha._init_logger adds handlers.
    # Logic in _init_logger: creates new handlers.
    # If not cleared, handlers multiply.
    # Let's verify behavior.
    assert len(nb.logger.handlers) == 2 # 1 File + 1 Stream.
    # If bind() just adds, it might be 4.
    # Current impl: self.logger.addHandler(...)
    # It does NOT clear existing handlers.
    # So calling bind() twice duplicates handlers!
    # This is a corner case behavior to document or assert.
    # Actually, logging.getLogger(name) returns same object.
    
    # Wait, check if expected behavior is to duplicate or replace.
    # Ideally replace. But for now assert current behavior.
    assert len(nb.logger.handlers) >= 2
    
    # Cleanup
    for h in nb.logger.handlers[:]:
        h.close()
        nb.logger.removeHandler(h)

def test_invalid_rotation_config_file(clean_env):
    """E2E Corner: Corrupt config file."""
    app_name = "E2E_BadConfig"
    root_dir = clean_env / ".Nibandha"
    config_dir = root_dir / "config"
    config_dir.mkdir(parents=True)
    
    (config_dir / "rotation_config.yaml").write_text("INVALID_YAML_CONTENT: :: [{")
    
    nb = Nibandha(AppConfig(name=app_name), root_name=str(root_dir))
    
    # Should handle error gracefully and probably return None or prompt
    # Since prompt is mocked or stdin not avail, it might crash if interactive?
    # In E2E we can't patch stdin easily unless we use mock.
    # Or expect it to fail if it tries to prompt.
    
    # Use RotationManager directly to verify load_config handles bad yaml
    from nibandha.core.rotation.infrastructure.manager import RotationManager
    import logging

    # Need to mimic bind setup partially
    rm = RotationManager(nb.config_dir, nb.app_root, logging.getLogger("test_corner"))
    
    conf = rm.load_config()
    # RotationManager.load_config catches generic exception and logs warning, returns None
    assert conf is None
