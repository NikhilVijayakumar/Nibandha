import sys
from pathlib import Path

def verify_documentation_structure(root_path: str):
    """
    Verifies that all modules in docs/features follow the Trinity structure:
    - functional/
    - technical/
    - test/
    """
    root = Path(root_path)
    docs_modules = root / "docs" / "features"
    
    if not docs_modules.exists():
        print(f"❌ Docs root not found: {docs_modules}")
        return False
        
    violations = []
    
    for module_dir in docs_modules.iterdir():
        if not module_dir.is_dir():
            continue
            
        mod_name = module_dir.name
        
        # Check Trinity
        func_dir = module_dir / "functional"
        tech_dir = module_dir / "technical"
        test_dir = module_dir / "test" # Note: test docs can be here or in global docs/test? 
        # The new standard puts them in docs/modules/{mod}/test OR docs/test/{mod}
        # Based on scaffold_docs.py update, we put them in docs/modules/{mod}/test
        
        if not func_dir.exists():
            violations.append(f"{mod_name}: Missing 'functional' directory")
        if not tech_dir.exists():
            violations.append(f"{mod_name}: Missing 'technical' directory")
        if not test_dir.exists():
            # Check fallback global docs/test/{mod}
            # This logic mimics DocumentationReporter somewhat
            fallback = root / "docs" / "test" / mod_name
            if not fallback.exists():
                violations.append(f"{mod_name}: Missing 'test' directory (checked local and global)")
                
    if violations:
        print("❌ Documentation Structure Violations:")
        for v in violations:
            print(f"  - {v}")
        return False
        
    print("✅ Documentation structure is compliant.")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_structure.py [project_root]")
        sys.exit(1)
        
    if not verify_documentation_structure(sys.argv[1]):
        sys.exit(1)
