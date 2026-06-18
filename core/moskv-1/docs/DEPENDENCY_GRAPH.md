# CORTEX_EXECUTIVE_GRAPH (L3)

> [!IMPORTANT]
> Topología extraída y sellada para la fase de Ejecución (L3).

```mermaid
graph TD
  distill_manifesto["distill_manifesto"]
  epigenetic_store["epigenetic_store"]
  exergy_sensor["exergy_sensor"]
  kernel["kernel"]
  kernel_board_of_directors["kernel/board_of_directors"]
  kernel_cortex_event_log["kernel/cortex_event_log"]
  kernel_cortex_schema["kernel.cortex_schema"]
  kernel_cortex_schema["kernel/cortex_schema"]
  kernel_cortex_watchdog["kernel/cortex_watchdog"]
  kernel_cronos_scheduler["kernel/cronos_scheduler"]
  kernel_dashboard_ui["kernel/dashboard_ui"]
  kernel_event_projector["kernel/event_projector"]
  kernel_reality_auditor["kernel/reality_auditor"]
  lancedb["lancedb"]
  moskv_1_auditor["moskv_1.auditor"]
  moskv_1_brain["moskv_1.brain"]
  moskv_1_crystallize_context["moskv_1.crystallize_context"]
  moskv_1_event_bus["moskv_1.event_bus"]
  moskv_1_exergy["moskv_1.exergy"]
  moskv_1_immunity["moskv_1.immunity"]
  moskv_1_memory["moskv_1.memory"]
  moskv_1_mpc_controller["moskv_1.mpc_controller"]
  moskv_1_super_agents["moskv_1.super_agents"]
  neo4j["neo4j"]
  osint_evolution_engine["osint_evolution_engine"]
  quorum_bus["quorum_bus"]
  reddit_monitoring_swarm["reddit_monitoring_swarm"]
  redteam_auditor["redteam_auditor"]
  sortu_apex_forge["sortu_apex_forge"]
  src_moskv_1___init__["src/moskv_1/__init__"]
  src_moskv_1_api["src/moskv_1/api"]
  src_moskv_1_auditor["src/moskv_1/auditor"]
  src_moskv_1_brain["src/moskv_1/brain"]
  src_moskv_1_crystallize_context["src/moskv_1/crystallize_context"]
  src_moskv_1_event_bus["src/moskv_1/event_bus"]
  src_moskv_1_exergy["src/moskv_1/exergy"]
  src_moskv_1_immunity["src/moskv_1/immunity"]
  src_moskv_1_memory["src/moskv_1/memory"]
  src_moskv_1_mpc_controller["src/moskv_1/mpc_controller"]
  src_moskv_1_super_agents["src/moskv_1/super_agents"]
  src_moskv_kernel["src/moskv_kernel"]
  src_redteam_auditor["src/redteam_auditor"]
  src_sortu_apex_forge["src/sortu_apex_forge"]
  kernel_cortex_event_log --> kernel_cortex_schema
  kernel_cronos_scheduler --> kernel
  kernel_event_projector --> kernel_cortex_schema
  osint_evolution_engine --> epigenetic_store
  src_moskv_1___init__ --> moskv_1_brain
  src_moskv_1___init__ --> moskv_1_event_bus
  src_moskv_1___init__ --> moskv_1_immunity
  src_moskv_1___init__ --> moskv_1_memory
  src_moskv_1___init__ --> moskv_1_super_agents
  src_moskv_1_api --> moskv_1_event_bus
  src_moskv_1_auditor --> moskv_1_event_bus
  src_moskv_1_brain --> moskv_1_event_bus
  src_moskv_1_event_bus --> moskv_1_exergy
  src_moskv_1_exergy --> moskv_1_event_bus
  src_moskv_1_memory --> lancedb
  src_moskv_1_memory --> moskv_1_auditor
  src_moskv_1_memory --> moskv_1_event_bus
  src_moskv_1_memory --> moskv_1_immunity
  src_moskv_1_memory --> neo4j
  src_moskv_1_mpc_controller --> redteam_auditor
  src_moskv_1_mpc_controller --> sortu_apex_forge
  src_moskv_1_super_agents --> moskv_1_brain
  src_moskv_1_super_agents --> moskv_1_event_bus
  src_moskv_kernel --> exergy_sensor
  src_moskv_kernel --> moskv_1_brain
  src_moskv_kernel --> moskv_1_crystallize_context
  src_moskv_kernel --> moskv_1_event_bus
  src_moskv_kernel --> moskv_1_memory
  src_moskv_kernel --> moskv_1_mpc_controller
  src_moskv_kernel --> redteam_auditor
  src_moskv_kernel --> sortu_apex_forge
```
