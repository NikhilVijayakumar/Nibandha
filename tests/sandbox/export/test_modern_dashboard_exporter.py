
import pytest
from pathlib import Path
from nibandha.export.infrastructure.modern_dashboard_exporter import ModernDashboardExporter

from tests.sandbox.export.utils import create_sandbox_env

def test_dashboard_export_rendering(export_sandbox):
    """Test that dashboard template renders with data."""
    # We need a template_dir that actually contains the jinja templates.
    # The real ones are in src/nikhil/nibandha/export/infrastructure/templates/dashboard
    # We can rely on default behavior pointing to src/..., but in sandbox we might not have access if not installed?
    # Actually the code uses __file__.parent relative paths, so it should work if source code is present.
    
    exporter = ModernDashboardExporter()
    
    # Setup environment
    env = create_sandbox_env(export_sandbox, {"export": {"formats": ["html"], "output_filename": "dashboard"}})
    output_dir = env['output']
    
    import json
    config_path = env['config_path']
    with open(config_path, 'r') as f:
        config_data = json.load(f)
    fname = config_data['export']['output_filename']

    sections = [
        {
            "title": "Section 1",
            "content": "<p>Content 1</p>",
            "metrics_cards": [{"title": "Metric 1", "value": "100"}]
        }
    ]
    
    # output_dir from env is correct
    
    output = output_dir / f"{fname}.html"
    
    # This might fail if templates are missing in the environment or path resolution is wrong in sandbox.
    # If it fails, we know we need to copy templates or fix pathing.
    try:
        exporter.export(sections, output, project_info={"name": "Test Project"})
        
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert "Section 1" in text
        assert "Content 1" in text
        assert "Metric 1" in text
        assert "Test Project" in text
    except Exception as e:
        pytest.fail(f"Dashboard export failed: {e}")

