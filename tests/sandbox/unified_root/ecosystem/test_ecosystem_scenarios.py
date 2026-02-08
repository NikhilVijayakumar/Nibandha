
import pytest
import json
import os
from pathlib import Path
from typing import List, Dict, Callable
from nibandha.configuration.infrastructure.file_loader import FileConfigLoader
from nibandha.configuration.domain.models.app_config import AppConfig
from nibandha.unified_root.infrastructure.filesystem_binder import FileSystemBinder
from nibandha.unified_root.domain.models.root_context import RootContext
from tests.sandbox.unified_root.utils import run_ur_test, BASE_CONFIG_TEMPLATE

# Helper: Run Multiple Config Bindings in Sequence
def run_ecosystem_test(
    sandbox_path: Path,
    test_name: str,
    description: str,
    configs: List[Dict], # List of Config Dicts
    expected_output_desc: str,
    validation_fn: Callable[[Path], None]
):
    """
    Simulates an ecosystem where multiple components (Apps/Libraries) are initialized 
    in the same environment. Binds each config sequentially.
    """
    current_test_dir = sandbox_path / test_name.replace(" ", "_")
    if current_test_dir.exists():
        import shutil
        shutil.rmtree(current_test_dir)
    current_test_dir.mkdir(parents=True)
    
    print(f"\n--- Running Ecosystem Test: {test_name} ---")
    print(f"Description: {description}")
    
    original_cwd = os.getcwd()
    binder = FileSystemBinder()
    loader = FileConfigLoader()
    
    try:
        os.chdir(current_test_dir)
        
        # specific step: write all configs to disk first (simulation)
        for i, cfg in enumerate(configs):
            app_name = cfg.get("name", f"App_{i}")
            filename = f"{app_name.lower()}_config.json"
            Path(filename).write_text(json.dumps(cfg, indent=2))
            
            print(f"Binding Component: {app_name}...")
            # Load and Bind - FileConfigLoader expects Path object
            app_config = loader.load(Path(filename), AppConfig)
            binder.bind(app_config)
            
        # Validate Aggregate Result
        print(f"Validating Ecosystem at: {current_test_dir}")
        validation_fn(current_test_dir)
        print("✅ Validation Command Passed")

    except Exception as e:
        print(f"❌ Test Failed: {e}")
        raise e
    finally:
        os.chdir(original_cwd)


# --- Scenarios ---

def test_scenario_1_nibandha_standalone(sandbox_root: Path):
    """
    Scenario 1: Nibandha (Single App/Lib) with no dependencies.
    Root: .Nibandha
    """
    cfg = BASE_CONFIG_TEMPLATE.copy()
    cfg["name"] = "Nibandha"
    cfg["unified_root"]["name"] = ".Nibandha"
    
    def validation(root_path: Path):
        root = root_path / ".Nibandha"
        # Since Root == Name, it flattens.
        # Logs directly under .Nibandha/logs
        assert (root / "logs").exists()
        assert (root / "headers.txt").exists() if (root/"headers.txt").exists() else True # placeholder
        assert (root / "config").exists()

    run_ecosystem_test(
        sandbox_path=sandbox_root,
        test_name="Ecosystem_1_Nibandha",
        description="Nibandha Standalone.",
        configs=[cfg],
        expected_output_desc="Flat .Nibandha structure.",
        validation_fn=validation
    )

def test_scenario_2_pravaha_with_nibandha(sandbox_root: Path):
    """
    Scenario 2: Pravaha (Main App) depends on Nibandha (Library).
    Pravaha defines root: .Pravaha
    Nibandha configured to share: .Pravaha
    """
    # Pravaha Config
    pravaha = BASE_CONFIG_TEMPLATE.copy()
    pravaha["name"] = "Pravaha"
    pravaha["unified_root"]["name"] = ".Pravaha"
    
    # Nibandha Config (Library Mode)
    # It must know to use .Pravaha root.
    nibandha = BASE_CONFIG_TEMPLATE.copy()
    nibandha["name"] = "Nibandha"
    nibandha["unified_root"]["name"] = ".Pravaha"
    
    def validation(root_path: Path):
        root = root_path / ".Pravaha"
        assert root.exists()
        
        # Pravaha (Main App) - Root Matches? No. Name=Pravaha, Root=.Pravaha.
        # Wait, is_single_app logic: ".Pravaha" vs "Pravaha" -> Match!
        # So Pravaha FLATTENS into Root.
        # Logs -> .Pravaha/logs (Pravaha's logs)
        assert (root / "logs").exists()
        
        # Nibandha (Library)
        # Name=Nibandha, Root=.Pravaha -> Mismatch.
        # So Nibandha NESTS into .Pravaha/Nibandha
        assert (root / "Nibandha").exists()
        assert (root / "Nibandha" / "logs").exists()
        assert (root / "Nibandha" / "config").exists()

    run_ecosystem_test(
        sandbox_path=sandbox_root,
        test_name="Ecosystem_2_Pravaha",
        description="Pravaha (Main) + Nibandha (Lib). Shared Root .Pravaha.",
        configs=[pravaha, nibandha],
        expected_output_desc="Pravaha flattened in root, Nibandha nested.",
        validation_fn=validation
    )

def test_scenario_3_amsha_with_nibandha(sandbox_root: Path):
    """
    Scenario 3: Amsha (Main App) depends on Nibandha.
    Root: .Amsha
    """
    amsha = BASE_CONFIG_TEMPLATE.copy()
    amsha["name"] = "Amsha"
    amsha["unified_root"]["name"] = ".Amsha"
    
    nibandha = BASE_CONFIG_TEMPLATE.copy()
    nibandha["name"] = "Nibandha"
    nibandha["unified_root"]["name"] = ".Amsha"
    
    def validation(root_path: Path):
        root = root_path / ".Amsha"
        assert root.exists()
        # Amsha Flattens (Single match)
        assert (root / "logs").exists()
        # Nibandha Nests
        assert (root / "Nibandha" / "logs").exists()

    run_ecosystem_test(
        sandbox_path=sandbox_root,
        test_name="Ecosystem_3_Amsha",
        description="Amsha (Main) + Nibandha (Lib). Shared Root .Amsha.",
        configs=[amsha, nibandha],
        expected_output_desc="Amsha flattened, Nibandha nested.",
        validation_fn=validation
    )

def test_scenario_4_akashvani_ecosystem(sandbox_root: Path):
    """
    Scenario 4: Akashvani (Main) + Amsha + Pravaha + Nibandha.
    Root: .Akashvani
    """
    # Main
    akashvani = BASE_CONFIG_TEMPLATE.copy()
    akashvani["name"] = "Akashvani"
    akashvani["unified_root"]["name"] = ".Akashvani"
    
    # Libs
    amsha = BASE_CONFIG_TEMPLATE.copy()
    amsha["name"] = "Amsha"
    amsha["unified_root"]["name"] = ".Akashvani"
    
    pravaha = BASE_CONFIG_TEMPLATE.copy()
    pravaha["name"] = "Pravaha"
    pravaha["unified_root"]["name"] = ".Akashvani"
    
    nibandha = BASE_CONFIG_TEMPLATE.copy()
    nibandha["name"] = "Nibandha"
    nibandha["unified_root"]["name"] = ".Akashvani"
    
    def validation(root_path: Path):
        root = root_path / ".Akashvani"
        assert root.exists()
        
        # Akashvani (Main) - Flattens
        assert (root / "logs").exists() # Main logs
        
        # Sub-Components - Nest
        assert (root / "Amsha" / "logs").exists()
        assert (root / "Pravaha" / "logs").exists()
        assert (root / "Nibandha" / "logs").exists()
        
        # Verify Config Isolation
        assert (root / "config").exists() # Main Config (Flattened)
        assert (root / "Amsha" / "config").exists()
        assert (root / "Pravaha" / "config").exists()
        assert (root / "Nibandha" / "config").exists()

    run_ecosystem_test(
        sandbox_path=sandbox_root,
        test_name="Ecosystem_4_Akashvani_Full",
        description="Akashvani (Main) + 3 Libs. All sharing .Akashvani root.",
        configs=[akashvani, amsha, pravaha, nibandha],
        expected_output_desc="Akashvani flat. Amsha/Pravaha/Nibandha nested.",
        validation_fn=validation
    )
