# Original User Request

## Initial Request — 2026-06-16T14:04:55+02:00

Build the sellable product "Moskv-1" from scratch and establish a robust, test-driven Python architecture.

Working directory: ~/teamwork_projects/moskv_1
Integrity mode: benchmark

## Requirements

### R1. Architecture & Scaffolding
Initialize the Moskv-1 project from scratch. Create the foundational directory structure and core modules.

### R2. Python Dependency Management
Strict adherence to the C5-REAL `managing-python-dependencies` protocol. Never use global pip installs. You must set up an explicit local environment (e.g., using `uv`, `poetry`, or `python -m venv .venv`).

### R3. Test-Driven Foundation
Write an automated test suite (e.g., using `pytest`) from day 1. All core logic implemented must have corresponding unit tests.

## Acceptance Criteria

### Automated Verification
- [ ] A local Python environment is successfully isolated and defined (e.g., `requirements.txt`, `pyproject.toml`).
- [ ] The automated test suite runs via the isolated environment and passes with 100% success.
- [ ] The project structure successfully runs a basic entry point script without crashing.
