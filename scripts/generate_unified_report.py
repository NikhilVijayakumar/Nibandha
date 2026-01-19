from pathlib import Path
from nibandha.reporting import ReportGenerator

def main():
    # Define paths
    root_dir = Path(__file__).resolve().parent.parent
    output_dir = root_dir / ".Nibandha" / "Nibandha" / "Report"
    docs_dir = root_dir / "docs" / "test"
    
    # Initialize Generator
    # We use the library default templates for now, or we could point to docs/test/templates 
    # if we wanted to keep them separate, but we moved them to the package.
    generator = ReportGenerator(
        output_dir=str(output_dir),
        docs_dir=str(docs_dir)
    )
    
    # Run Generation
    # nibandha self-test targets
    generator.generate_all(
        unit_target="tests/unit", 
        e2e_target="tests/e2e",
        package_target="src/nikhil/nibandha"
    )

if __name__ == "__main__":
    main()
