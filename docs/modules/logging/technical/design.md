# Logging Module: Technical Design

## Design Decisions
We use standard library `logging` configured via dictConfig for flexibility.
- **JSON Formatting**: For machine readability (Splunk/ELK ready).
- **Console Output**: Human-readable colored output for CLI usage.
- **Rotation**: Time-based rotation ensures logs don't consume infinite disk space.

## Data Flow
`Application Code` -> `logger.info()` -> `LogHandler` -> `Formatter` -> `File/Console`.

## Contracts
Follows Python's `logging` protocol. Custom protocols defined in `domain/protocols/logging_protocol.py`.
