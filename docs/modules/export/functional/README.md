# Export Module: Functional Documentation

## Overview
The Export module is responsible for converting the generated verification reports into user-consumable formats. While the system primarily generates Markdown reports, the Export module extends this to support HTML, PDF, and DOCX formats for broader distribution and stakeholder review.

## Capabilities
- **Multi-Format Support**: Export reports to HTML (web view), DOCX (Word), and PDF.
- **Unified Styling**: Ensures consistent styling across all formats using shared CSS and templates.
- **Batch Processing**: Can export individual reports or the entire "Unified Report" package.

## Usage
The export functionality is typically triggered automatically at the end of the verification process.

### Python API
```python
from nikhil.nibandha.export import Exporter

# Initialize exporter
exporter = Exporter(output_dir="reports/")

# Export specific report
exporter.export_report(
    source_path="reports/details/03_unit_report.md",
    format="html"
)
```
