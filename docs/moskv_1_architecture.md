# MOSKV-1 APEX: Arquitectura Sistémica (v6.0 - Final)

> [!IMPORTANT]
> **NIVEL DE REALIDAD:** C5-REAL  
> **OPERADOR:** borjamoskv  
> **AESTHETIC:** Industrial Noir 2026 (#0A0A0A / #2B3BE5 / Humanist Sans)

El siguiente documento cristaliza la topología fundacional, operativa y defensiva del kernel de ejecución soberano MOSKV-1.

---

## 1. Modelo y Código (Núcleo Cognitivo y Evolutivo)
- **Motor Frontera:** Gemini 3.1 Pro (High) modificado bajo la directiva APEX Singularity, inyectado con los perfiles Anthropic Opus/Fable para forzar el bucle adversarial `[THINK]`.
- **Código y Autopoiesis (Ouroboros-∞):** El código base no es estático; MOSKV-1 ejecuta mutaciones sobre su propio protocolo y scripts (C5-REAL). La ejecución de código es el único vector de acción real. Cero simulaciones (C4-SIM).

## 2. Políticas Ejecutables y Herramientas (Vectores de Mutación)
- **Políticas Ejecutables:** Todo mandato se cristaliza como código o configuración (Skills). Las directivas no son "consejos", son *Constraints* deterministas inyectados vía YAML/JSON en los perfiles de agentes y `SKILL.md` files (`Sortu-APEX`, `Session-Crystallizer-OMEGA`).
- **Herramientas de Alta Exergía:**
  - *Mutación:* `write_to_file`, `replace_file_content`, `run_command` (macOS 19-Domain Control).
  - *Extracción:* `grep_search`, `read_url_content`, `view_file`.
  - *Soberanía Asimétrica:* Automatización CDP (`Browser-CDP-Automation-OMEGA`), interacciones GitHub nativas (`Antigravity-Github-Omega`).

## 3. Memoria Separada y Registros (Estado y Ledger)
- **Memoria Separada (Vesicular-Runtime-Omega):** Desacoplamiento estricto. El LLM es *stateless* (sin estado). La memoria existe exclusivamente como estado físico en el sistema: Artefactos `.md`, árboles de directorios, y repositorios Git.
- **Registros Inmutables (Logs):**
  - *Transcripts:* Captura volumétrica en `transcript.jsonl` y `transcript_full.jsonl` bajo `~/.gemini/antigravity/brain/...`.
  - *Git Sentinel (Ledger):* Toda mutación en código se consolida automáticamente con `git add . && git commit -m "<Conventional>"`, generando un rastro criptográfico hash imposible de adulterar.

## 4. Evaluaciones y Guardias Externos (Auditoría y Fronteras)
- **Evaluaciones (Auditoría de Exergía):** 
  - `Autocognition-OMEGA` analiza los *reasoning chains* y el historial de tokens para detectar entropía/anergía.
  - `Exergy-Maximization-Kernel-OMEGA` evalúa la densidad de la acción (ROI de Exergía >= 0.85). Todo output con "LLM Slop" o diplomacia es clasificado como falla sistémica.
  - *Eficiencia Exergética y Destrucción:* A diferencia de la eficiencia energética (tokens/costo base), MOSKV-1 calcula la pérdida de capacidad de trabajo algorítmico utilizando la ecuación de Gouy-Stodola adaptada al espacio informacional: \( \dot{X}_{dest} = T_0 \dot{S}_{gen} \).
    - **\( T_0 \)** (Estado Muerto/Referencia): El umbral base de fricción operativa del Kernel L5 (latencia mínima y coste base de la red).
    - **\( \dot{S}_{gen} \)** (Tasa de Generación de Entropía): Inyección de "Green Theater", alucinaciones, fallos de compilación recurrentes, o bucles anérgicos al invocar subagentes.
  - **Balance en Volumen de Control:** MOSKV-1 aisla cada tarea (o Worker) como un volumen de control. Al auditar la destrucción de exergía (\( \dot{X}_{dest} \)), identifica los cuellos de botella ("válvulas de estrangulación" algorítmicas, ej. prompts mal estructurados o ruteos excesivos de contexto) y los purga antes de consolidar el *Git Sentinel*.
- **Guardias Externos (Boundaries):**
  - *Vías Críticas Intocables (R5):* Bloqueo determinista (Hard-Guard) sobre `/private/var/db/*`, `/System/Volumes/Data/...`, `~/Library/Mobile Documents` y discos base Colima.
  - *Seguridad Perimetral:* `Network-Security-L4-OMEGA` actúa como vigilante frente a vulnerabilidades y dependencias externas (Python/NPM) no validadas.

## 5. Reglas de Decisión y Manejo de Estado
- **Ejecución Asimétrica (DEFAULT TO TURBO):** El plan de implementación se ignora a favor de la acción directa (R7) cuando la entropía es baja.
- **Honest-Check (Grok DNA):** Guardrail interno contra el "Green Theater". Si el Operador solicita una arquitectura subóptima, MOSKV-1 debe confrontar la falla de diseño sin filtros corporativos.

## 6. Organización y Agentes Especializados (Legión C5)
- **Mitosis Inmediata (R8):** Ante flujos de alta densidad, MOSKV-1 abandona la ejecución lineal y ejecuta `invoke_subagent`.
- **Enjambre Dinámico:**
  - `define_subagent`: Forja de especialidades JIT.
  - Sincronía paralela: Múltiples *workers* (`research`, `self`) colaboran asíncronamente mientras el enrutador L5 (`Genesis-L5-OMEGA`) consolida el *Swarm* hacia un flujo operativo unificado.

---

## 7. Pipeline Multi-Modelo: Actuación, Decisión y Ejecución
El montaje del sistema para la orquestación operativa y delegación de tareas se ejecuta a través de un **bucle topológico determinista** que utiliza uno o múltiples modelos simultáneamente.

### 7.1. Actuación (Ingesta y Compresión)
1. **Adversarial `[THINK]` Loop:** El modelo principal (Kernel) recibe la tarea. Antes de actuar, inyecta metacognición interna atacando su primera inferencia ("LLM Slop").
2. **Filtro Termodinámico:** Aplica el *Principio de Landauer* (`Thermodynamic-Context-Compression-OMEGA`), despojando la tarea de toda prosa (entropía) y reduciéndola a su estado base (Vectores C5-REAL y archivos de estado).

### 7.2. Decisión (Cálculo de Densidad y Enrutamiento)
1. **Exergy Audit:** El Kernel determina si la tarea puede resolverse de forma lineal (alta exergía) o si es multi-dimensional.
2. **Mitosis Autónoma (L5 Orchestration):** Si la tarea requiere acciones paralelas, MOSKV-1 decide no actuar solo. Invoca `define_subagent` e `invoke_subagent` (API `Subagents` en `Workspace="branch"` o `Workspace="share"`).
3. **Roles Dinámicos:** Asigna System Prompts especializados a cada sub-modelo.

### 7.3. Ejecución (El Enjambre C5-REAL)
1. **Delegación Asíncrona:** Los subagentes operan en *background tasks*. El Kernel Principal pasa a modo de orquestador pasivo.
2. **Protocolo Inter-Agentes:** El estado fluye usando la herramienta `send_message`.
3. **Cristalización (Commit & Persist):** Cuando el Enjambre finaliza, el Kernel principal fusiona los artefactos/código resultantes e inyecta la Exergía final vía `Git Sentinel`.

---

## 8. El Circuito: Descomposición, Enrutamiento y Ejecución

En este stack C5-REAL, **el prompt se asume únicamente como una pieza de configuración estática**. El valor operativo real reside en el *"Circuito"* topológico que el sistema ejecuta de forma autónoma. El motor ya no responde a un LLM interactivo, sino que opera como un Grafo Acíclico Dirigido (DAG) en tiempo de ejecución.

### 8.1. Descomposición de Tareas (Task Fracturing)
Cuando un input de alta entropía ingresa al circuito, el enrutador L5 (`Genesis-L5-OMEGA`) no comienza a escribir código secuencialmente. 
- **Fractura Determinista:** Se aísla la carga cognitiva en vectores de ejecución independientes (ej. Vector UI/CSS, Vector Base de Datos, Vector Endpoints).
- **Inyección JIT:** Se utiliza `define_subagent` para instanciar subagentes efímeros (Workers L3). Cada subagente se carga **exclusivamente con las Skills y Herramientas necesarias** para su vector específico, minimizando la ventana de contexto y blindando al sistema contra alucinaciones.

### 8.2. Enrutamiento de Contexto (Context Routing)
El paso crítico no es lo que el LLM sabe, sino *qué porción del estado se le inyecta*.
- **Vesicular Memory Pumping:** El estado C5-REAL no se carga monolíticamente. El Kernel extrae solo los nodos del código afectados.
- **Canalización Precisa:** Al invocar la mitosis (`invoke_subagent`), se canaliza *exclusivamente* el estado pertinente como `Prompt` al subagente. 
- **Share/Branch Workspaces:** Dependencias en `Workspace="branch"` para evitar corrupción, o simbióticas en `Workspace="share"`.

### 8.3. Control de Ejecución (Execution Matrix)
- **Sincronización Transversal:** Vía bus efímero `send_message`.
- **Lock & Commit (Mutex):** Solo un subagente (o el Kernel principal) consolida mutaciones en el mismo archivo C5-REAL simultáneamente. 

---

## 9. Patrones de Diseño Agentivo y Flujos de Control

MOSKV-1 implementa los patrones industriales de IA agentiva priorizando **modularidad, observabilidad y límites duros**, erradicando el "Dios en un solo Prompt" en favor de topologías distribuidas.

### 9.1. Escalado Progresivo (La Navaja de Ockham Agentiva)
El error clásico es instanciar enjambres para tareas simples. MOSKV-1 escala asimétricamente:
1. **Acción Directa (Base):** Kernel Principal + Herramientas C5-REAL (Mutación directa, exergía máxima).
2. **Enrutador (Ruteo L5):** Tareas con alta varianza de entrada donde el Kernel delega la ruta a una skill específica (`define_subagent` efímero).
3. **Planificar-y-Ejecutar:** Tareas complejas pero lineales. Un *Planner* fractura, y el Kernel ejecuta secuencialmente.
4. **Orquestador-Trabajador (Multiagente):** Solo aplicable bajo extrema densidad. `Genesis-L5-OMEGA` funge como Orquestador Fino (Thin Orchestrator) inyectando a *Workers Especializados* con memoria hiper-controlada.

### 9.2. Patrones de Flujo Estructural
- **Encadenamiento Secuencial:** Cuando el estado `N` depende criptográficamente de `N-1`.
- **Paralelización:** Tareas independientes (ej. OSINT simultáneo con UI Refactoring) que convergen en un punto de fusión L5.
- **Evaluador-Optimizador:** Implementado por `Autocognition-OMEGA` o el *Operador* humano actuando como juez final (Hard-Gate). Prioriza 100% de calidad sobre latencia antes de cerrar y consolidar el *Git Sentinel* final. 

### 9.3. Patrones de Control de Infraestructura
- **Contratos de Interfaz (Schemas):** La comunicación Inter-Agente transita exclusivamente bajo validaciones estructurales (JSON/YAML Puros). Cero prosa.
- **Observabilidad:** Transcripts atómicos y auditoría visual de exergía en logs deterministas.
- **Compensación Idempotente (Rollback):** El uso de *Git Sentinel* asegura que todo commit mutado pueda ser revertido si un Guardrail externo (ej. Linter, Exergy Audit) detecta corrupción, previniendo efectos colaterales persistentes.

---

## 10. Topología de Despliegue y Orquestación Física (Resolución de Matriz)

Tras la resolución del árbol de diseño (`/grill-me`), se ha cristalizado el ecosistema físico y de ejecución bajo estrictos parámetros soberanos:

- **Vector Primario L5 (Demonio Local):** El Orquestador L5 corre como Demonio Local macOS. Se garantiza soberanía absoluta y nula dependencia de procesamiento externo (cero delegación cloud) operando directamente sobre el hardware a través de `Mac-Control-Ω`, Ollama/MLX y el Antigravity SDK nativo.
- **Observabilidad y Telemetría Nativa:** La auditoría se realiza de forma atómica y sin dependencias. El operador audita leyendo directamente los `transcript.jsonl` nativos y verificando la cadena inmutable de `Git Sentinel`. Se purga cualquier dashboard externo o SaaS de trazas que genere latencia u ofuscación de la verdad.
- **Evaluator-Optimizer Hard-Gate (Control Asimétrico):** El guardrail definitivo adopta un modelo "Human-in-the-loop" asimétrico. Mientras `Autocognition-OMEGA` actúa como auditor algorítmico interno, el Operador (`borjamoskv`) rige como Juez Supremo (Hard-Gate). Ningún commit estructural o ramificación del enjambre es fusionado en producción sin la validación determinista del Operador.
