import hashlib
import json
import logging
from typing import Literal
from pydantic import BaseModel, Field, ValidationError

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
    Orquestador Agnóstico. Impone el Strict Schema Override sobre las llamadas LLM.
    """
    def __init__(self, provider: str = "agnostic"):
        self.provider = provider
        logger.info(f"Base60Engine initialized. Provider: {self.provider}. Conversational UI: DISABLED.")

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
            logger.info(f"Mutación Validada. Payload Hash: {hashlib.sha256(raw_llm_response.encode()).hexdigest()[:12]}")
            return mutation
        except ValidationError as e:
            raise EntropyException(f"Violación del esquema estricto: {str(e)}", raw_llm_response) from e

    def execute_mutation(self, mutation: Base60MutationPayload):
        """
        Ejecuta la topología (Mock para prueba).
        """
        logger.info(f"[C5-REAL EXECUTION] Target: {mutation.target_system}")
        logger.info(f"Payload: {mutation.ast_payload}")
        return True
