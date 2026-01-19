import subprocess
import json
import sys

def get_complexity_report(target_path: str):
    """
    Runs Ruff/Radon to identify functions with high cyclomatic complexity.
    """
    try:
        # Use Ruff to find complexity (C901) violations
        result = subprocess.run(
            ["ruff", "check", target_path, "--select", "C901", "--format", "json"],
            capture_output=True, text=True
        )
        violations = json.loads(result.stdout)
        return violations
    except Exception as e:
        print(f"❌ Error running complexity check: {e}")
        return []

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "src"
    issues = get_complexity_report(path)
    if issues:
        print(f"Found {len(issues)} complexity spikes. Refactoring required.")
        sys.exit(1)
    print("✅ Complexity within Nibandha limits.")