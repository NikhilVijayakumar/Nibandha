
import pytest
import json
from pathlib import Path
from nibandha.unified_root.domain.models.root_context import RootContext
import copy
from tests.sandbox.unified_root.utils import run_ur_test, BASE_CONFIG_TEMPLATE

def test_single_config_multi_library_organization(sandbox_root: Path):
    """
    REAL-WORLD Scenario: Pravaha (Main App) with Nibandha (Library Dependency)
    
    Key Points:
    - Only ONE AppConfig (Pravaha's)
    - Creates folders for BOTH Pravaha and Nibandha
    - Uses custom_structure for library folders
    - Uses explicit paths for main app organization
    """
    config_data = copy.deepcopy(BASE_CONFIG_TEMPLATE)
    config_data["name"] = "Pravaha"
    config_data["unified_root"] = {
        "name": ".Pravaha",
        "custom_structure": {
            # Main app organization
            "app": {
                "data": {},
                "cache": {},
                "temp": {}
            },
            # Library folders
            "nibandha": {
                "logs": {},
                "cache": {}
            },
            # Optional: other dependencies
            "other_lib": {
                "data": {}
            }
        }
    }
    
    # Direct Pravaha's resources to app/ subfolder
    config_data["logging"]["log_dir"] = ".Pravaha/app"  # Binder creates app/logs
    config_data["reporting"]["output_dir"] = ".Pravaha/app/Report"
    
    def validation(context: RootContext, root_path: Path):
        root = root_path / ".Pravaha"
        
        # Pravaha's organized structure
        assert (root / "app" / "logs").exists(), "Pravaha logs should be in app/"
        assert (root / "app" / "Report").exists(), "Pravaha reports should be in app/"
        assert (root / "app" / "data").exists()
        assert (root / "app" / "cache").exists()
        
        # Nibandha's library folders (created via custom_structure)
        assert (root / "nibandha" / "logs").exists(), "Nibandha folder created for library"
        assert (root / "nibandha" / "cache").exists()
        
        # Other lib placeholder
        assert (root / "other_lib" / "data").exists()
        
        # Config should NOT be created
        assert not (root / "config").exists()
        
        print("\n[OK] Structure Created Successfully:")
        print(".Pravaha/")
        print("|-- app/")
        print("|   |-- logs/        (Pravaha's logs)")
        print("|   |-- Report/      (Pravaha's reports)")
        print("|   |-- data/")
        print("|   |-- cache/")
        print("|   +-- temp/")
        print("|-- nibandha/")
        print("|   |-- logs/        (Reserved for Nibandha)")
        print("|   +-- cache/")
        print("|-- other_lib/")
        print("|   +-- data/")
        print("+-- (config/ folder removed)")

    run_ur_test(
        sandbox_path=sandbox_root,
        test_name="Practical_Single_Config_Multi_Lib",
        description="Single AppConfig creates organized folders for main app + dependencies",
        input_config_content=json.dumps(config_data, indent=2),
        expected_output_desc="Organized structure with app/ and library-specific folders",
        validation_fn=validation
    )


def test_akashvani_full_ecosystem_single_config(sandbox_root: Path):
    """
    COMPLEX Scenario: Akashvani with 3 dependencies (Amsha, Pravaha, Nibandha)
    Uses ONLY Akashvani's AppConfig to create all folders
    """
    config_data = copy.deepcopy(BASE_CONFIG_TEMPLATE)
    config_data["name"] = "Akashvani"
    config_data["unified_root"] = {
        "name": ".Akashvani",
        "custom_structure": {
            "app": {
                "logs": {},
                "Report": {},
                "models": {},
                "data": {}
            },
            "amsha": {
                "logs": {},
                "cache": {}
            },
            "pravaha": {
                "logs": {},
                "flows": {}
            },
            "nibandha": {
                "logs": {},
                "reports": {}
            }
        }
    }
    
    config_data["logging"]["log_dir"] = ".Akashvani/app"
    config_data["reporting"]["output_dir"] = ".Akashvani/app/Report"
    
    def validation(context: RootContext, root_path: Path):
        root = root_path / ".Akashvani"
        
        # Akashvani's resources
        assert (root / "app" / "logs").exists()
        assert (root / "app" / "Report").exists()
        assert (root / "app" / "models").exists()
        
        # All 3 libraries have their folders
        assert (root / "amsha" / "logs").exists()
        assert (root / "pravaha" / "logs").exists()
        assert (root / "nibandha" / "logs").exists()
        
        print("\n[OK] Full Ecosystem Structure:")
        print(".Akashvani/")
        print("|-- app/             (Akashvani's resources)")
        print("|   |-- logs/")
        print("|   |-- Report/")
        print("|   |-- models/")
        print("|   +-- data/")
        print("|-- amsha/           (Amsha library)")
        print("|   |-- logs/")
        print("|   +-- cache/")
        print("|-- pravaha/         (Pravaha library)")
        print("|   |-- logs/")
        print("|   +-- flows/")
        print("|-- nibandha/        (Nibandha library)")
        print("|   |-- logs/")
        print("|   +-- reports/")
        print("+-- (config/ folder removed)")

    run_ur_test(
        sandbox_path=sandbox_root,
        test_name="Practical_Akashvani_Ecosystem",
        description="Single config creates full ecosystem structure",
        input_config_content=json.dumps(config_data, indent=2),
        expected_output_desc="Complete ecosystem with app/ and 3 library folders",
        validation_fn=validation
    )
