# CR-002: Security Scanning Module (SAST)

## 1. Summary
Integrate a **Static Application Security Testing (SAST)** module into `Nibandha` to proactively detect security vulnerabilities.

## 2. Problem Statement
Current quality checks focus on structure and style, leaving security vulnerabilities (like weak crypto or safe execution violations) undetected until manual review or external penetration testing.

## 3. Proposed Solution
Integrate `bandit` (or similar AST-based security scanner) into the reporting pipeline.

### Core Checks
1.  **Injection Vulnerabilities**: SQL injection, Command injection.
2.  **Weak Cryptography**: Usage of md5, sha1, or hardcoded keys.
3.  **System Safety**: Usage of `assert` in production code (which is optimized out in `-O` mode).
4.  **Serialization**: Unsafe YAML/Pickle loading.

### Implementation Details
-   **Wrapper**: Create `SecurityReporter` that wraps `bandit` execution.
-   **Output**: New report `05_security_report.md`.
-   **Thresholds**: Fail build on HIGH severity issues.

## 4. Value Proposition
-   **Security Baseline**: Ensures every Nibandha-based project meets a minimum security standard.
-   **Shift Left**: Catches vulnerabilities at commit-time.
