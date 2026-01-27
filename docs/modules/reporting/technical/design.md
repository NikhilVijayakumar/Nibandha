# Reporting Module: Technical Design

## Design Decisions
The reporting engine uses a **Builder Pattern** (`UnitDataBuilder`, `E2EDataBuilder`) to construct report data objects, decoupled from rendering.
- **Jinja2**: For flexible, logic-free template rendering.
- **Markdown-First**: Reports are generated as Markdown for Git compatibility, then exported.

## Data Flow
`Test Results (JSON)` -> `DataBuilder` -> `Enriched Data Dictionary` -> `TemplateEngine` -> `Markdown Report`.

## Contracts
`ReporterProtocol` ensures all reporters (Unit, E2E, Quality) expose a consistent `generate()` interface.
