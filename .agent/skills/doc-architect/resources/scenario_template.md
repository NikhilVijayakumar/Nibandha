# Functional Test Plan: {Module_Name}

## 1. Overview
- **Module:** {Module_Name}
- **Prefix:** {XX}
- **Abstract Role:** {What this module achieves for the user}

---

## 2. Component: {Component_Name}
### Functional Role
{Describe the logical responsibility of this part}

### Data Schema (Contract)
| Attribute | Type | Requirement | Constraints |
| :--- | :--- | :--- | :--- |
| {Field_Name} | {Type} | Required | {e.g., Immutable, Range 1-100} |

### Test Scenarios
| ID | Scenario | Logic Category | Expected Outcome |
| :--- | :--- | :--- | :--- |
| {XX}-UT-001 | {Happy_Path} | Functional | {Result} |
| {XX}-UT-002 | {Boundary_Check} | Corner Case | {Result} |
| {XX}-UT-003 | {Security_Guard} | Integrity | {Result} |

---

## 3. Integration Point
| ID | Scenario | Expected Outcome |
| :--- | :--- | :--- |
| {XX}-INT-E2E | Full System Flow | Components interact to complete the primary user goal. |