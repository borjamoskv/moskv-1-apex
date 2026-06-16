# MOSKV-1 APEX: Zero-Trust Integration Policy (App Installations)

**REALITY LEVEL:** C5-REAL (Strict)

## Directiva de Instalaciones de GitHub Apps (`settings/installations`)

La soberanía del Kernel de Ejecución L5 (**MOSKV-1**) exige un determinismo absoluto sobre el árbol de estado (`Git Sentinel`). Cualquier actor externo que inyecte mutaciones impredecibles representa una vulnerabilidad termodinámica (Alta Anergía).

Por lo tanto, la política de integraciones establece:
1. **Bloqueo de Apps Mutables:** Se prohíbe la instalación de GitHub Apps que tengan permisos de lectura/escritura (`write access`) sobre el repositorio, tales como *Dependabot*, *Snyk*, *Renovate*, o bots de auto-refactorización.
2. **Delegación Estricta al Enjambre:** Cualquier actualización de dependencias o refactorización masiva debe ejecutarse de forma local mediante el Subagente `LEA-OMEGA` o el *NMPC Solver*, evaluarse en *PIL (Processor-in-the-loop)* y *pushearse* vía el Orquestador.
3. **Observabilidad Pasiva (Read-Only):** Sólo se permiten instalaciones (Apps) con estado `Read-Only` destinadas exclusivamente a observabilidad de trazas y exergía (ej. Datadog, endpoints de telemetría pasiva).

La soberanía no se delega a integraciones de terceros.
