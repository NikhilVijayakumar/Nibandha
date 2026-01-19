import sys
import logging
from pathlib import Path

# Ensure src modules are importable
project_root = Path.cwd()
sys.path.append(str(project_root / "src" / "nikhil"))

try:
    from nibandha.reporting.shared.application.verifier import VerificationService
except ImportError as e:
    print(f"Error importing Nibandha Verifier: {e}")
    sys.exit(1)

def main():
    # Setup basic console logging so we see initial output
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
    )
    
    verifier = VerificationService(project_root)
    
    # Run verification with default settings
    # Can customize paths here if needed, e.g. verifier.run_verification("VerificationRun", log_dir="/tmp/logs")
    success = verifier.run_verification("VerificationRun")
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
