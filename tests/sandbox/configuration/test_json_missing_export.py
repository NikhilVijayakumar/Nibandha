
import pytest
from nibandha.configuration.domain.models.app_config import AppConfig
from tests.sandbox.configuration.utils import run_config_test

def test_json_missing_export(sandbox_root):
    """
    Scenario: 'export' section is missing from app_config.json
    Expected: AppConfig loads successfully, 'export' field has default values.
    """
    # app_config without "export"
    config_data = {
        "name": "NoExportApp",
        "mode": "dev"
        # "export": ... MISSING
    }

    def validation(result: AppConfig):
        assert result.name == "NoExportApp"
        # Check default export config
        assert result.export is not None
        assert result.export.formats == ["md", "html"] # The default we set in model
        assert result.export.output_filename == "report"

    import json
    run_config_test(
        sandbox_path=sandbox_root,
        test_name="MissingExportConfig",
        description="Verify app loads with default export config when section is missing.",
        input_filename="app_config.json",
        input_content=json.dumps(config_data),
        expected_output_desc="AppConfig with default export settings",
        action=lambda p: AppConfig.model_validate_json(p.read_text()),
        validation=validation
    )

