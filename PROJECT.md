# Project: Moskv-1 Python Core

## Architecture
- Foundational Python implementation of the Moskv-1 cognitive architecture.
- Modular layout including event loop/bus, brain region executors, and memory interfaces.
- Standard packaging using `pyproject.toml` and `.venv` isolation.

## Code Layout
- `src/moskv_1/`: Main source package
  - `__init__.py`: Entry point and versioning
  - `event_bus.py`: Hash-chained event bus for message passing
  - `brain.py`: Brain region executor and Swarm nodes
  - `memory.py`: Neo4j/graph or local crystallized memory store interface
- `tests/`: Automated unit and integration tests
  - `test_event_bus.py`
  - `test_brain.py`
  - `test_memory.py`
- `pyproject.toml`: Project configuration and dependency matrix
- `.venv/`: Local virtual environment

## Interface Contracts
- `EventBus`: `publish(payload: dict) -> CortexEvent`, `subscribe(topic: str, callback: Callable)`
- `CortexEvent`: Wrapper containing `hash: str`, `prev_hash: str`, `timestamp: float`, `payload: dict`
- `BrainRegion`: `run()`, `process_event(event: CortexEvent)`
- `MemoryStore`: `crystallize(event: CortexEvent)`, `prune(entropy_threshold: float)`

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | M1. Exploration | Environment discovery and design verification | None | DONE |
| 2 | M2. Scaffolding & Env | Local venv setup and project files scaffolding | M1 | DONE |
| 3 | M3. Implementation | Core Python logic (EventBus, BrainRegion, MemoryStore) | M2 | DONE |
| 4 | M4. Verification | Pytest execution, review, challenge, forensic audit | M3 | DONE |
| 5 | M5. Rebranding & UI | Rebrand landing page to AGENTS.ARCHI under Industrial Noir 2026 guidelines | M4 | DONE |
| 6 | M6. Vercel-Cloudflare | CDN caching rules, security bypasses, and redirect loop resolution | M5 | DONE |
| 7 | M7. Dynamic Sandbox | Hashing-based deterministic OSINT mockup telemetry engine | M6 | DONE |
| 8 | M8. Manifesto Modal UX | Copy-to-clipboard button overlays in technical code blocks | M7 | DONE |
| 9 | M9. Telemetry Injection Bridge | Real-time C5-REAL SSE telemetry bridge (FastAPI) | M8 | DONE |
