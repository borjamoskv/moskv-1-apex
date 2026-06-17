# [C5-REAL] Exergy-Maximized
import math
from collections import Counter
from enum import Enum
from typing import Tuple

class ImmuneState(Enum):
    OBSERVED = "observed"
    QUARANTINED = "quarantined"
    PROMOTABLE = "promotable"
    SEALED = "sealed"
    NECROTIC = "necrotic"
    AMPUTATED = "amputated"

class ImmunityLayer:
    """
    MOSKV-1 Python Core Immunity Layer.
    Detects, quarantines, and manages semantic necrosis and low-information-density signals.
    """
    def __init__(self, high_threshold: float = 3.5, mid_threshold: float = 2.5):
        self.high_threshold = high_threshold
        self.mid_threshold = mid_threshold

    @staticmethod
    def calculate_entropy(text: str) -> float:
        """Computes Shannon entropy (bits per character) of a string."""
        if not text:
            return 0.0
        counts = Counter(text)
        total = len(text)
        return -sum((c / total) * math.log2(c / total) for c in counts.values() if c > 0)

    def evaluate_signal(self, text: str) -> Tuple[ImmuneState, float]:
        """
        Evaluates a signal based on Shannon entropy threshold.
        Returns the target ImmuneState and the raw entropy score.
        """
        entropy = self.calculate_entropy(text)
        if entropy >= self.high_threshold:
            return ImmuneState.PROMOTABLE, entropy
        elif entropy >= self.mid_threshold:
            return ImmuneState.QUARANTINED, entropy
        else:
            return ImmuneState.NECROTIC, entropy
