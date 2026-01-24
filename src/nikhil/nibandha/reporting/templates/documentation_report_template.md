# Documentation Status Report

## 📅 Summary
> **Date:** {{date}}

| Overall Grade | Functional | Technical | Test |
| :---: | :---: | :---: | :---: |
| <span style="font-size: 2em; color: {{grade_color}}">{{display_grade}}</span> | {{func_grade}} | {{tech_grade}} | {{test_grade}} |

## 📊 Overview

Overview of documentation coverage and drift.

{{charts}}

> [!NOTE]
> **Drift** indicates the age difference between the documentation file and the last modification of the code module. High drift (>90 days) suggests documentation might be outdated.

## 📦 Detailed Breakdown

### Functional Documentation (`docs/modules`)
Coverage: {{func_coverage}}%

| Module | Status | Drift (Days) |
| :--- | :---: | :---: |
{{func_table}}

### Technical Documentation (`docs/technical`)
Coverage: {{tech_coverage}}%

| Module | Status | Drift (Days) |
| :--- | :---: | :---: |
{{tech_table}}

### Test Documentation (`docs/test`)
Coverage: {{test_coverage}}%

| Module | Unit Scenarios | E2E Scenarios | Drift (Days) |
| :--- | :---: | :---: | :---: |
{{test_table}}

## 🔍 Missing Documentation

Below is a list of critical modules that completely lack documentation.

{{missing_section}}
