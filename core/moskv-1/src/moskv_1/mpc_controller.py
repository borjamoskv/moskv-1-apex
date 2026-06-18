#!/usr/bin/env python3
import ast
import os
from typing import List
from sortu_apex_forge import SwarmVector
from redteam_auditor import ExergyAuditor

class CognitiveNMPC:
    def __init__(self, Q: float = 1.0, R: float = 0.2, lmbda: float = 0.1):
        self.Q = Q
        self.R = R
        self.lmbda = lmbda

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
        print("\n=== NMPC MITOSIS OPTIMIZATION LOOP ===")
        for v in proposed_vectors:
            exergy_score = self.evaluate_template_ast(v.logic)
            anergy = 1.0 - exergy_score
            compute_volume = len(v.logic) * 0.01
            cost_j = (self.Q * anergy) + (self.lmbda * compute_volume)
            print(f"  Candidate: {v.role} | Virtual Exergy: {exergy_score:.2f} | Cost J: {cost_j:.4f}")
            if exergy_score >= 0.85:
                optimized.append(v)
            else:
                print(f"  [NMPC-PRUNED] Candidate '{v.role}' rejected due to excessive predicted Anergia.")
        scale_cost = self.R * (len(optimized) ** 2)
        print(f"  Optimized Swarm Size: {len(optimized)} | Scale Penalty: {scale_cost:.4f}")
        return optimized
