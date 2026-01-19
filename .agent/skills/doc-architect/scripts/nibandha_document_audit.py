import os
from pathlib import Path


def run_document_audit():
    root = Path(".")
    src_path = root / "src"
    docs_base = root / "docs" / "modules"

    # Header Branding
    print("\n" + "=" * 70)
    print("📋  NIBANDHA DOCUMENTATION HEALTH AUDIT")
    print("=" * 70)
    print(f"{'MODULE NAME':<25} | {'STATUS':<12} | {'MISSING COMPONENTS'}")
    print("-" * 70)

    if not src_path.exists():
        print("❌ Error: 'src/' directory not found. Are you in the project root?")
        return

    # Filter for actual logic modules (exclude __pycache__, etc.)
    modules = [d for d in src_path.iterdir() if d.is_dir() and not d.name.startswith((".", "__"))]

    if not modules:
        print("No modules found in src/.")
        return

    for mod in modules:
        mod_name = mod.name

        # Check for core artifacts
        has_readme = (docs_base / mod_name / "README.md").exists()
        has_test_specs = (root / "docs" / "test" / mod_name).exists()

        missing = []
        if not has_readme: missing.append("README.md")
        if not has_test_specs: missing.append("Test Scenarios")

        status = "✅ HEALTHY" if not missing else "❌ DEBT"
        missing_str = ", ".join(missing) if missing else "None"

        print(f"{mod_name:<25} | {status:<12} | {missing_str}")

    print("-" * 70)
    print("👉 Action: Use 'Document [Module]' to generate missing blueprints.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_document_audit()