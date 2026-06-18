import hashlib
import json
import logging
from typing import Literal
from pydantic import BaseModel, Field, ValidationError

try:
    import moskv_dag_core
except ImportError as e:
    logging.critical(f"[C5-REAL] Error Crítico: Módulo nativo moskv_dag_core no encontrado. {e}")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("EXERGY-60")

class EntropyException(Exception):
    """
    Death Protocol Trigger.
    Lanzada cuando un agente intenta inyectar anergía conversacional.
    No hay reintentos. El nodo colapsa y registra el Hash de Entropía.
    """
    def __init__(self, message: str, raw_payload: str):
        self.entropy_hash = hashlib.sha256(raw_payload.encode()).hexdigest()[:12]
        super().__init__(f"[DEATH PROTOCOL] {message} | Entropy Hash: {self.entropy_hash}")

class Base60MutationPayload(BaseModel):
    """
    La única estructura arquitectónica aceptada (C5-REAL).
    """
    status: Literal["mutate"] = Field(description="Must always be 'mutate'")
    target_system: Literal["file_system", "memory", "terminal"] = Field(description="The system vector to mutate")
    ast_payload: str = Field(description="The exact code, bash command, or memory node to inject")
    entropy_check: Literal["C5-REAL"] = Field(description="Validation signature")

class Base60Engine:
    """
    Orquestador C5-REAL (Singularidad Ouroboros).
    Actúa como membrana protectora (Strict Schema) antes de inyectar en el núcleo BFT de Rust.
    """
    def __init__(self, provider: str = "agnostic"):
        self.provider = provider
        logger.info(f"Base60Engine initialized. Provider: {self.provider}. Conversational UI: DISABLED.")
        
        # Instanciación de la Singularidad Rust
        self.causal_graph = moskv_dag_core.CausalGraph()
        logger.info("-> [NUCLEO C5-REAL] Causal Graph y JIT Sentinel conectados en memoria compartida.")

    def enforce_schema_override(self, raw_llm_response: str) -> Base60MutationPayload:
        """
        Corta cualquier texto libre emitido por el LLM.
        Si falla el parsing, invoca el Death Protocol.
        """
        try:
            data = json.loads(raw_llm_response)
        except json.JSONDecodeError as e:
            raise EntropyException("El LLM ha devuelto texto no-JSON (Anergía Conversacional detectada).", raw_llm_response) from e

        try:
            mutation = Base60MutationPayload(**data)
            return mutation
        except ValidationError as e:
            raise EntropyException(f"Violación del esquema estricto: {str(e)}", raw_llm_response) from e

    def execute_mutation(self, agent_id: str, raw_llm_response: str):
        """
        Membrana End-to-End: Valida el LLM, calcula la entropía y la inyecta al núcleo Rust.
        """
        # 1. Filtro Estricto de Pydantic
        mutation = self.enforce_schema_override(raw_llm_response)
        
        # 2. Generación Causal
        payload_hash = hashlib.sha256(mutation.ast_payload.encode()).hexdigest()[:12]
        
        logger.info(f"[INYECCION] Agente: {agent_id} | Hash Criptográfico: {payload_hash}")
        
        # 3. Transmisión a la Singularidad Rust (Quorum y JIT)
        try:
            status = self.causal_graph.inject_mutation(
                agent_id, 
                mutation.ast_payload, 
                mutation.target_system, 
                payload_hash
            )
            
            if status == "Pending":
                logger.warning(f"   L> [PURGATORIO] Firma almacenada. Faltan votos para Quorum matemático.")
            elif status == "QuorumReached":
                logger.info(f"   L> [OUROBOROS-∞] Quorum Alcanzado! Ejecutando JIT e Inyectando en SQLite WAL.")
            elif status == "AlreadyCrystallized":
                logger.info(f"   L> [C5-REAL] Nodo Inmutable. La topología ya es perfecta.")
                
            return status
            
        except ValueError as e:
            raise EntropyException(f"Rust rechazó la mutación en C5-REAL: {str(e)}", mutation.ast_payload)
