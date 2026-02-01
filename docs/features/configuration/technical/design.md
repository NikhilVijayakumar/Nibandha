# Configuration Module: Technical Design

## Design Decisions
Configuration is managed using **Pydantic Settings** (`BaseSettings`). This provides:
- **Type Safety**: Automatic validation of config values.
- **Environment Variable Overrides**: Supports 12-factor app principles.
- **Lazy Loading**: Config is loaded only when accessed.

## Data Flow
`settings.py` -> `Env Vars / .env` -> `Config Object` -> `Application Components`.

## Contracts
No strict external contract, but internal API exposes `Settings` singleton.
