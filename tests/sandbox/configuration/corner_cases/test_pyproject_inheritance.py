
import pytest
import os
from pathlib import Path
from nibandha.configuration.domain.models.app_config import AppConfig
from nibandha.configuration.infrastructure.file_loader import FileConfigLoader
from tests.sandbox.configuration.utils import run_config_test

def test_pyproject_inheritance(sandbox_root: Path):
    loader = FileConfigLoader()
    
    # 1. Define dummy pyproject.toml content
    # We define a custom project name and package structure
    pyproject_content = """
    [project]
    name = "CustomProject"
    version = "1.0.0"
    
    [tool.setuptools.package-dir]
    "" = "src/custom_lib"
    """
    
    # 2. Config file that should inherit defaults (empty fields)
    input_content = """
    mode: "dev"
    # name is missing -> should come from pyproject
    # reporting.quality_target missing -> should come from package-dir
    """
    
    def action(input_file):
        # Setup: Write pyproject.toml to the input directory
        # The input_file is in sandbox_root/input/inheritance_config.yaml
        base_dir = input_file.parent
        (base_dir / "pyproject.toml").write_text(pyproject_content, encoding="utf-8")
        
        # We need to switch CWD so AppConfig.resolve_paths finds our pyproject.toml
        # because it uses Path.cwd()
        original_cwd = os.getcwd()
        try:
            os.chdir(base_dir)
            # Load config - validation happens here, so resolve_paths runs here
            return loader.load(input_file, AppConfig)
        finally:
            # Restore CWD
            os.chdir(original_cwd)
        
    def validation(config):
        # 1. Verify Project Name Inheritance
        assert config.name == "CustomProject", f"Expected 'CustomProject', got '{config.name}'"
        
        # 2. Verify Quality Target Inheritance (from tool.setuptools.package-dir)
        # The logic in resolve_paths checks for "" or "." being mapped to a dir
        # We mapped "" = "src/custom_lib"
        assert config.reporting.quality_target == "src/custom_lib"
        
        # 3. Verify Package Roots Inheritance (from project name)
        # Default behavior uses project name lowercased
        assert "customproject" in config.reporting.package_roots

        # 4. Verify Unified Root Name Default
        # Should default to .CustomProject because Name changed
        assert config.unified_root.name == ".CustomProject"

    run_config_test(
        sandbox_path=sandbox_root,
        test_name="Pyproject.toml Inheritance",
        description="Verify AppConfig inherits defaults (name, package dir) from the current pyproject.toml.",
        input_filename="inheritance_config.yaml",
        input_content=input_content,
        expected_output_desc="AppConfig with values inherited from the mock pyproject.toml.",
        action=action,
        validation=validation
    )

def test_pyproject_missing_fallback(sandbox_root: Path):
    loader = FileConfigLoader()
    
    # Config file with no overrides, no pyproject.toml scenarios essentially tested by general tests
    # But specifically ensuring no crash if pyproject is missing is a good corner case
    
    input_content = "mode: 'dev'"
    
    def action(input_file):
        # Ensure NO pyproject.toml exists in this directory (safe because sandbox input dir is clean)
        # We explicitly chdir to a clean dir
        original_cwd = os.getcwd()
        try:
            os.chdir(input_file.parent)
            return loader.load(input_file, AppConfig)
        finally:
            os.chdir(original_cwd)
            
    def validation(config):
        # Should fall back to hardcoded defaults
        assert config.name == "Nibandha"
        assert config.reporting.quality_target == "src"
        assert config.reporting.package_roots == [] # Or handled safely

    run_config_test(
        sandbox_path=sandbox_root,
        test_name="Pyproject.toml Missing (Fallback)",
        description="Verify robust fallback when pyproject.toml is absent.",
        input_filename="no_pyproject.yaml",
        input_content=input_content,
        expected_output_desc="AppConfig with hardcoded defaults ('Nibandha', 'src').",
        action=action,
        validation=validation
    )
