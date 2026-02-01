# Unified Root Module: Technical Design

## Design Decisions
This module serves as the **Composition Root** or Orchestrator.
- **Facade**: Provides a unified interface to run verification suites.
- **Dependency Injection**: Wires together Reporters, Exporters, and Config at runtime.

## Data Flow
`CLI / Script` -> `VerificationApp` -> `Reporters` -> `Aggregator` -> `Conclusion Report`.

## Contracts
Public API entry points for CI/CD integration.
