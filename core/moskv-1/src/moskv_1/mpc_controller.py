#!/usr/bin/env python3
import ast
import os
import sqlite3
import json
from typing import List, Tuple
from sortu_apex_forge import SwarmVector
from redteam_auditor import ExergyAuditor

class CognitiveRLNMPC:
    """
    C5-REAL Reinforcement Learning NMPC.
    Autopoietically adjusts Q, R, and lambda based on temporal difference exergy yields.
    """
    def __init__(self, db_path: str = ".agents/rl_state.db", alpha: float = 0.05):
        self.db_path = db_path
        self.alpha = alpha
        self._init_db()
        self.Q, self.R, self.lmbda = self._load_weights()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        return conn

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with self._get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS rl_weights (
                    id INTEGER PRIMARY KEY,
                    q_weight REAL,
                    r_weight REAL,
                    lambda_weight REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS exergy_ledger (
                    id INTEGER PRIMARY KEY,
                    predicted_exergy REAL,
                    actual_exergy REAL,
                    reward REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor = conn.execute("SELECT COUNT(*) FROM rl_weights")
            if cursor.fetchone()[0] == 0:
                conn.execute("INSERT INTO rl_weights (q_weight, r_weight, lambda_weight) VALUES (1.0, 0.2, 0.1)")

    def _load_weights(self) -> Tuple[float, float, float]:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT q_weight, r_weight, lambda_weight FROM rl_weights ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            return row if row else (1.0, 0.2, 0.1)

    def _update_weights(self, reward: float):
        # Q-learning proxy: Shift parameters towards gradients that maximize Reward
        self.Q = max(0.1, self.Q + self.alpha * reward * (1.0 - self.Q))
        self.R = max(0.05, self.R - self.alpha * reward * 0.1)
        self.lmbda = max(0.01, self.lmbda - self.alpha * reward * 0.05)
        
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO rl_weights (q_weight, r_weight, lambda_weight) VALUES (?, ?, ?)",
                (self.Q, self.R, self.lmbda)
            )

    def reinforce(self, predicted_exergy: float, actual_exergy: float):
        """Temporal Difference update based on execution outcome."""
        reward = actual_exergy - predicted_exergy
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO exergy_ledger (predicted_exergy, actual_exergy, reward) VALUES (?, ?, ?)",
                (predicted_exergy, actual_exergy, reward)
            )
        self._update_weights(reward)

    def evaluate_template_ast(self, logic: str) -> float:
        try:
            from sortu_apex_forge import SortuApexMitosis, SwarmVector
            temp_vector = SwarmVector(role="Temp", logic=logic, target_module="temp")
            forge = SortuApexMitosis()
            code_template = forge._generate_agent_ast(temp_vector)
            tree = ast.parse(code_template)
            auditor = ExergyAuditor()
            auditor.visit(tree)
            return float(auditor.score)
        except Exception:
            return 0.0

    def optimize_mitosis(self, proposed_vectors: List[SwarmVector]) -> List[SwarmVector]:
        optimized: List[SwarmVector] = []
        print("\n=== C5-REAL RL-NMPC MITOSIS OPTIMIZATION LOOP ===")
        print(f"  [RL-Weights] Q: {self.Q:.4f} | R: {self.R:.4f} | Lambda: {self.lmbda:.4f}")
        for v in proposed_vectors:
            exergy_score = self.evaluate_template_ast(v.logic)
            anergy = 1.0 - exergy_score
            compute_volume = len(v.logic) * 0.01
            cost_j = (self.Q * anergy) + (self.lmbda * compute_volume)
            
            print(f"  Candidate: {v.role} | Predict Exergy: {exergy_score:.2f} | Cost J: {cost_j:.4f}")
            if exergy_score >= 0.85:
                optimized.append(v)
            else:
                print(f"  [RL-PRUNED] Candidate '{v.role}' rejected. Exergy < 0.85.")
                
        scale_cost = self.R * (len(optimized) ** 2)
        print(f"  Optimized Swarm Size: {len(optimized)} | Scale Penalty: {scale_cost:.4f}")
        return optimized

# Mantener compatibilidad de API para scripts C4-SIM
CognitiveNMPC = CognitiveRLNMPC

