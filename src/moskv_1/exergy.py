import json
import time
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from moskv_1.event_bus import CortexEvent

class ExergyMeter:
    def __init__(self, token_cost_weight: float = 0.001, starvation_decay_factor: float = 0.05):
        self.token_cost_weight = token_cost_weight
        self.starvation_decay_factor = starvation_decay_factor
    def estimate_anergy(self, payload: dict) -> float:
        """
        Estimates the Anergy (friction/cost) of processing the payload.
        Uses string length as a surrogate for token processing cost.
        """
        base_anergy = float(payload.get("anergy", 1.0))
        content = payload.get("content", "")
        if isinstance(content, (dict, list)):
            content_str = json.dumps(content)
        else:
            content_str = str(content)
        token_estimate = len(content_str) / 4.0
        cost = token_estimate * self.token_cost_weight
        return base_anergy + cost
    def calculate(self, event: "CortexEvent") -> float:
        """
        Calculates the thermodynamic Exergy score of an event.
        E = (Expected_Value * Novelty * Urgency) / (Anergy + 1)
        """
        payload = event.payload
        expected_value = float(payload.get("expected_value", 1.0))
        novelty = float(payload.get("novelty", 1.0))
        urgency = float(payload.get("urgency", 1.0))
        anergy = self.estimate_anergy(payload)
        exergy = (expected_value * novelty * urgency) / (anergy + 1.0)
        return exergy
    def get_priority_score(self, event: "CortexEvent", queue_time: float) -> float:
        """
        Returns the min-heap priority score (negative is higher priority).
        Applies a temporal decay factor to prevent starvation of low-priority tasks.
        """
        base_exergy = self.calculate(event)
        wait_time = time.time() - queue_time
        if wait_time < 0:
            wait_time = 0.0
        decayed_exergy = base_exergy * (1.0 + (wait_time * self.starvation_decay_factor))
        return -decayed_exergy
