# MOSKV-1 APEX: M10 Freeze Contract
**Reality Level:** C5-REAL  
**Timestamp:** 2026-06-18  

## 1. Topología del Workspace
El directorio raíz (`/`) adopta una partición termodinámica inmutable:
- `core/moskv-1/`: Entorno sellado del OS y Back-end. Única fuente de verdad de Ledgers y Runtime (Python).
- `apps/`: Interfaces consumidoras. Alojamiento del Front-End productivo (`apps/agents.archi`) y dominios satélites.
- `archive/legacy/`: Cripta exergética inerte, comprimida mediante el pre-commit hook de empaquetado para aislar la entropía inactiva.

## 2. Definición Estricta del Ledger EventEnvelope
La estructura base del NATS y memory `EventBus` (`CortexEvent`) no puede ser mutada sin una votación de la junta de consenso.
```json
{
  "hash": "str (SHA-256 det. serialization)",
  "prevHash": "str (Link al hash anterior)",
  "timestamp": "float (ms precision from epoch)",
  "payload": "dict (Unrestricted shape, mandatory JSON serialization)"
}
```

## 3. Aislamiento de Capa de Presentación (SSE)
La transferencia de telemetría a la interfaz UI (Vercel Node) opera en **Modo Sólo Emisión**.
- **`GET /api/v1/stream`**: Transporte asimétrico `append-only`.
- **Restricción de Flujo**: `write_events = false` en Frontend; `emit_only = true` en Backend.
- **Inyección Externa**: Cualesquiera inyecciones generadas desde la UI deben cruzar a través de microservicios segregados (ej. sub-swarms en `apps/`) autenticados independientemente.

## 4. Manifiestos de Despliegue
- **Front-End Vercel**: `apps/agents.archi/vercel.json` asume autoridad sobre ruteo estático, cache (`no-store`) y proxy functions para el dashboard web.
- **Microservicios Node**: Limitados explícitamente a su rol de capa Serverless.

## 5. Daemons y Ciclo de Vida (Lifecycle)
El ciclo del sistema se congela alrededor de los scripts nucleares:
- `moskv_wake.sh`: Inicia y reactiva el OS.
- `moskv_sleep.sh`: Captura el estado en `swarm_os.sqlite` y finaliza las rutinas en RAM.
- `cron_exergy_monitor.sh`: Daemon de salud persistente cada 5 minutos.
