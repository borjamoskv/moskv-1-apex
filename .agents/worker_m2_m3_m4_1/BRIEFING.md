# BRIEFING — 2026-06-16T14:09:20+02:00

## Mission
Implement local environment, scaffolding, core modules, and unit test suite for Moskv-1.

## 🔒 My Identity
- Archetype: teamwork_preview_worker
- Roles: implementer, qa, specialist
- Working directory: /Users/borjafernandezangulo/Documents/antigravity/lively-maxwell/.agents/worker_m2_m3_m4_1
- Original parent: c805a751-1ac5-488a-a638-d14d773a3864
- Milestone: Initialize python package, local environment, and test suite

## 🔒 Key Constraints
- CODE_ONLY network mode: No external network access.
- DO NOT CHEAT: No hardcoded test results, facade implementations.
- Write only to own folder for agent metadata, write to workspace root for source/tests.
- Maintain real state and behavior.

## Current Parent
- Conversation ID: c805a751-1ac5-488a-a638-d14d773a3864
- Updated: not yet

## Task Summary
- **What to build**: Moskv-1 core modules (`__init__.py`, `event_bus.py`, `brain.py`, `memory.py`) and tests (`test_event_bus.py`, `test_brain.py`, `test_memory.py`) in workspace root. Link to `~/teamwork_projects/moskv_1`. Configure Hatchling `pyproject.toml`.
- **Success criteria**: Local isolated virtual env set up, package installed, pytest passes 100%, conventional git commit made.
- **Interface contracts**: `/Users/borjafernandezangulo/Documents/antigravity/lively-maxwell/.agents/explorer_m1_2/`
- **Code layout**: `src/moskv_1/` and `tests/`

## Key Decisions Made
- Establish symbolic link in `~/teamwork_projects/moskv_1` pointing to the workspace root.
- Implement true mocks for NATS JetStream and Neo4j so tests can run in unit mode without containers.

## Change Tracker
- **Files modified**: None
- **Build status**: TBD
- **Pending issues**: None

## Quality Status
- **Build/test result**: TBD
- **Lint status**: TBD
- **Tests added/modified**: None

## Loaded Skills
- None

## Artifact Index
- /Users/borjafernandezangulo/Documents/antigravity/lively-maxwell/.agents/worker_m2_m3_m4_1/ORIGINAL_REQUEST.md — Original user request
