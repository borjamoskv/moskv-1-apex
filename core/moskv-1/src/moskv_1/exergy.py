import json
import time
import os
import sqlite3
from typing import Any, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from kernel.event_bus import CortexEvent

class DynamicExergyMeter:
    """
    C5-REAL Reinforcement Learning Exergy Meter.
    Autopoietically adjusts token_cost_weight and starvation_decay_factor via SQLite WAL state.
    """
    def __init__(self, db_path: str = ".agents/rl_state.db", alpha: float = 0.01):
        self.db_path = db_path
        self.alpha = alpha
        self._init_db()
        self.token_cost_weight, self.starvation_decay_factor = self._load_weights()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        return conn

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with self._get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS exergy_rl_weights (
                    id INTEGER PRIMARY KEY,
                    token_cost_weight REAL,
                    starvation_decay_factor REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor = conn.execute("SELECT COUNT(*) FROM exergy_rl_weights")
            if cursor.fetchone()[0] == 0:
                conn.execute("INSERT INTO exergy_rl_weights (token_cost_weight, starvation_decay_factor) VALUES (0.001, 0.05)")

    def _load_weights(self) -> Tuple[float, float]:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT token_cost_weight, starvation_decay_factor FROM exergy_rl_weights ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            return row if row else (0.001, 0.05)

    def reinforce(self, system_entropy: float):
        """
        RL Step: If entropy drops (negative system_entropy), we did well. 
        Adjust parameters to favor current decay/cost ratios.
        """
        reward = -system_entropy
        self.token_cost_weight = max(0.0001, self.token_cost_weight - (self.alpha * reward * 0.0005))
        self.starvation_decay_factor = max(0.01, self.starvation_decay_factor + (self.alpha * reward * 0.01))
        
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO exergy_rl_weights (token_cost_weight, starvation_decay_factor) VALUES (?, ?)",
                (self.token_cost_weight, self.starvation_decay_factor)
            )

    def estimate_anergy(self, payload: dict) -> float:
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
        payload = event.payload
        expected_value = float(payload.get("expected_value", 1.0))
        novelty = float(payload.get("novelty", 1.0))
        urgency = float(payload.get("urgency", 1.0))
        anergy = self.estimate_anergy(payload)
        exergy = (expected_value * novelty * urgency) / (anergy + 1.0)
        return exergy

    def get_priority_score(self, event: "CortexEvent", queue_time: float) -> float:
        base_exergy = self.calculate(event)
        wait_time = time.time() - queue_time
        if wait_time < 0:
            wait_time = 0.0
        decayed_exergy = base_exergy * (1.0 + (wait_time * self.starvation_decay_factor))
        return -decayed_exergy

# Override for strict C5-REAL compatibility
ExergyMeter = DynamicExergyMeter
