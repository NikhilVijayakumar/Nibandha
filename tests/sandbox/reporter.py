
import re
from pathlib import Path
from collections import defaultdict
import datetime

# Determine standard paths
TESTS_SANDBOX_DIR = Path(__file__).parent
PROJECT_ROOT = TESTS_SANDBOX_DIR.parent.parent
SANDBOX_ROOT = PROJECT_ROOT / ".sandbox"

def parse_report(report_path: Path):
    content = report_path.read_text(encoding="utf-8")
    
    # Extract Test Name
    # # Sandbox Test Report: <Name>
    name_match = re.search(r"# Sandbox Test Report: (.*)", content)
    test_name = name_match.group(1).strip() if name_match else "Unknown"

    # Extract Result
    # **Result**: PASS
    # **Result**: FAIL: ...
    result_match = re.search(r"\*\*Result\*\*: (PASS|FAIL.*)", content)
    result_line = result_match.group(1).strip() if result_match else "UNKNOWN"
    
    status = "PASS" if result_line.startswith("PASS") else "FAIL"
    # Capture details for failures, cleaning up newlines for table format
    detail = result_line if status == "FAIL" else ""
    
    return {
        "name": test_name,
        "status": status,
        "detail": detail,
        "path": report_path
    }

def generate_summary():
    if not SANDBOX_ROOT.exists():
        print(f"Sandbox Root not found at {SANDBOX_ROOT}")
        return

    reports = []
    print(f"Scanning {SANDBOX_ROOT} for report.md files...")
    for report_file in SANDBOX_ROOT.glob("**/report.md"):
        try:
            reports.append(parse_report(report_file))
        except Exception as e:
            print(f"Failed to parse {report_file}: {e}")

    # Group by Module
    # relative path from SANDBOX_ROOT: module/test_case/report.md
    # e.g. unified_root/happy_path/test_ur_happy/test_full_explicit_config/report.md
    # module = unified_root
    # We might want deeper granularity if module is e.g. "unified_root/happy_path"
    # But sticking to top-level folder inside .sandbox is safest for "Module" definition.
    
    modules = defaultdict(list)
    for r in reports:
        try:
            rel_path = r["path"].relative_to(SANDBOX_ROOT)
            if len(rel_path.parts) > 1:
                module_name = rel_path.parts[0]
                modules[module_name].append(r)
            else:
                modules["root"].append(r)
        except ValueError:
            continue

    # Generate Global Summary
    summary_lines = [
        "# Sandbox Test Summary",
        f"**Date**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Module Breakdown",
        "| Module | Total | Pass | Fail |",
        "|---|---|---|---|"
    ]

    total_tests = 0
    total_pass = 0
    total_fail = 0

    sorted_modules = sorted(modules.keys())

    for module in sorted_modules:
        tests = modules[module]
        n_pass = sum(1 for t in tests if t["status"] == "PASS")
        n_fail = sum(1 for t in tests if t["status"] == "FAIL")
        total = len(tests)
        
        total_tests += total
        total_pass += n_pass
        total_fail += n_fail

        summary_lines.append(f"| [{module}]({module}_summary.md) | {total} | {n_pass} | {n_fail} |")
        
        # Determine status icon
        icon = "✅" if n_fail == 0 else "❌"
        
        # Generate Module Detail
        module_lines = [
            f"# Test Module: {module} {icon}",
            "",
            f"**Total**: {total} | **Pass**: {n_pass} | **Fail**: {n_fail}",
            "",
            "## Test Cases",
            "| Test Name | Status | Detail |",
            "|---|---|---|"
        ]
        
        # Sort tests by name
        for t in sorted(tests, key=lambda x: x["name"]):
            status_icon = "✅" if t["status"] == "PASS" else "❌"
            # Link to the report file (relative to SANDBOX_ROOT where summary is)
            link = t["path"].relative_to(SANDBOX_ROOT).as_posix()
            
            # Clean detail for table
            clean_detail = t["detail"].replace("\n", " ").replace("|", r"\|")
            if len(clean_detail) > 100:
                clean_detail = clean_detail[:97] + "..."
                
            module_lines.append(f"| [{t['name']}]({link}) | {status_icon} {t['status']} | {clean_detail} |")

        # Write Module Summary
        module_summary_path = SANDBOX_ROOT / f"{module}_summary.md"
        module_summary_path.write_text("\n".join(module_lines), encoding="utf-8")
        print(f"Generated Module Summary: {module_summary_path}")

    summary_lines.extend([
        "",
        "## Totals",
        f"**Total Tests**: {total_tests}",
        f"**Passed**: {total_pass}",
        f"**Failed**: {total_fail}",
    ])

    summary_path = SANDBOX_ROOT / "summary.md"
    summary_path.write_text("\n".join(summary_lines), encoding="utf-8")
    print(f"Generated Global Summary: {summary_path}")

if __name__ == "__main__":
    generate_summary()
