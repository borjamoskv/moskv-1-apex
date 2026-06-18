import json

with open('/Users/borjafernandezangulo/.gemini/antigravity/brain/9b80ea63-c6db-4a94-b668-b8efc6e5389c/scratch/deps.json', 'w') as f:
    f.write('''{
  "exergy_sensor.py": ["os", "glob", "subprocess", "argparse", "sys", "re", "pathlib", "json"],
  "osint_evolution_engine.py": ["os", "epigenetic_store", "urllib.request", "time", "argparse", "socket", "email", "datetime", "ssl", "logging", "json"],
  "epigenetic_store.py": ["os", "hashlib", "sqlite3", "json"],
  "reddit_monitoring_swarm.py": ["os", "urllib.request", "time", "datetime", "logging", "json"],
  "quorum_bus.py": ["time", "sqlite3"],
  "distill_manifesto.py": ["os", "re", "json"],
  "kernel/dashboard_ui.py": ["rich.table", "rich.console", "time", "rich.text", "rich.layout", "rich.live", "rich.panel"],
  "kernel/cortex_event_log.py": ["os", "sys", "hashlib", "dataclasses", "datetime", "kernel.cortex_schema", "json"],
  "kernel/board_of_directors.py": ["os", "subprocess", "time", "sys", "datetime"],
  "kernel/cortex_watchdog.py": ["os", "platform", "subprocess", "shutil", "sys", "datetime", "json"],
  "kernel/event_projector.py": ["os", "sqlite3", "sys", "datetime", "kernel.cortex_schema", "json"],
  "kernel/cortex_schema.py": ["uuid", "time", "typing", "hashlib", "dataclasses", "datetime", "json"],
  "kernel/reality_auditor.py": ["typing", "re"],
  "kernel/cronos_scheduler.py": ["os", "signal", "subprocess", "time", "shlex", "sys", "fcntl", "re", "kernel", "datetime", "asyncio", "json"],
  "src/sortu_apex_forge.py": ["os", "time", "ast", "hashlib", "dataclasses"],
  "src/redteam_auditor.py": ["os", "glob", "time", "ast", "sys", "importlib.util"],
  "src/moskv_kernel.py": ["moskv_1.event_bus", "ctypes", "moskv_1.crystallize_context", "dataclasses", "glob", "enum", "moskv_1.brain", "redteam_auditor", "typing", "sys", "asyncio", "json", "hashlib", "exergy_sensor", "moskv_1.mpc_controller", "os", "subprocess", "time", "sortu_apex_forge", "moskv_1.memory"],
  "src/moskv_1/memory.py": ["os", "enum", "moskv_1.event_bus", "moskv_1.auditor", "time", "lancedb", "neo4j", "typing", "asyncio", "moskv_1.immunity", "json"],
  "src/moskv_1/__init__.py": ["moskv_1.event_bus", "moskv_1.brain", "moskv_1.memory", "moskv_1.super_agents", "moskv_1.immunity"],
  "src/moskv_1/event_bus.py": ["time", "typing", "moskv_1.exergy", "hashlib", "dataclasses", "asyncio", "json"],
  "src/moskv_1/api.py": ["moskv_1.event_bus", "fastapi", "sse_starlette.sse", "fastapi.middleware.cors", "asyncio"],
  "src/moskv_1/brain.py": ["moskv_1.event_bus", "time", "typing", "aiohttp", "asyncio"],
  "src/moskv_1/immunity.py": ["os", "enum", "math", "collections", "typing"],
  "src/moskv_1/mpc_controller.py": ["os", "redteam_auditor", "ast", "typing", "sortu_apex_forge"],
  "src/moskv_1/auditor.py": ["typing", "yaml", "moskv_1.event_bus", "dataclasses"],
  "src/moskv_1/exergy.py": ["typing", "time", "moskv_1.event_bus", "json"],
  "src/moskv_1/crystallize_context.py": ["os", "glob", "typing", "sys", "re", "pathlib", "json"],
  "src/moskv_1/super_agents.py": ["moskv_1.event_bus", "moskv_1.brain"]
}''')

with open('/Users/borjafernandezangulo/.gemini/antigravity/brain/9b80ea63-c6db-4a94-b668-b8efc6e5389c/scratch/deps.json') as f:
    data = json.load(f)

# Filter out standard library to keep graph clean
std_libs = {"os", "sys", "time", "datetime", "json", "typing", "ast", "hashlib", "subprocess", "argparse", "glob", "re", "pathlib", "socket", "email", "ssl", "logging", "sqlite3", "unittest.mock", "asyncio", "pytest", "secrets", "http.client", "urllib.request", "urllib.parse", "urllib.error", "yaml", "shutil", "platform", "signal", "shlex", "fcntl", "uuid", "dataclasses", "ctypes", "enum", "math", "collections", "fastapi", "sse_starlette.sse", "fastapi.middleware.cors", "aiohttp", "importlib.util", "rich.table", "rich.console", "rich.text", "rich.layout", "rich.live", "rich.panel"}

edges = set()
nodes = set()

def clean_name(name):
    return name.replace('/', '_').replace('.', '_').replace('-', '_')

for src, deps in data.items():
    src_node = src.replace('.py', '')
    src_clean = clean_name(src_node)
    nodes.add(f'{src_clean}["{src_node}"]')
    for dep in deps:
        if dep not in std_libs:
            dep_clean = clean_name(dep)
            nodes.add(f'{dep_clean}["{dep}"]')
            edges.add(f'{src_clean} --> {dep_clean}')

with open('core/moskv-1/docs/DEPENDENCY_GRAPH.md', 'w') as f:
    f.write("# CORTEX_EXECUTIVE_GRAPH (L3)\n\n")
    f.write("> [!IMPORTANT]\n> Topología extraída y sellada para la fase de Ejecución (L3).\n\n")
    f.write("```mermaid\ngraph TD\n")
    for n in sorted(list(nodes)):
        f.write(f"  {n}\n")
    for e in sorted(list(edges)):
        f.write(f"  {e}\n")
    f.write("```\n")
