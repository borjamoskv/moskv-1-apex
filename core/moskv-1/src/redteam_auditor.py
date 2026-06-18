import os
import ast
import glob
import time

# ==============================================================================
# AGENT-PAPER-REDTEAM (v1.0)
# OBJECTIVE: Hostile Logic Evaluation & Adversarial Audit
# CLASSIFICATION: C5-REAL
# ==============================================================================

class ExergyAuditor(ast.NodeVisitor):
    """
    Parses the AST of forged subagents to evaluate structural determinism.
    Any detection of non-deterministic loops or untyped logic yields negative exergy.
    """
    def __init__(self):
        self.score = 1.0  # Perfect Exergy Yield baseline
        self.violations = []

    def visit_While(self, node):
        # Open-ended while loops are heavily penalized (high risk of CoT infinite loops)
        self.score -= 0.3
        self.violations.append("Unbounded While Loop detected (-0.3)")
        self.generic_visit(node)
        
    def visit_FunctionDef(self, node):
        # Functions must have type hints for deterministic C5-REAL execution
        if not node.returns:
            self.score -= 0.15
            self.violations.append(f"Function '{node.name}' lacks return type annotation (-0.15)")
        self.generic_visit(node)
        
    def visit_Try(self, node):
        # Bare excepts hide state mutations
        for handler in node.handlers:
            if handler.type is None:
                self.score -= 0.2
                self.violations.append("Bare Except detected. Masks failure states (-0.2)")
        self.generic_visit(node)

    def visit_Import(self, node):
        import importlib.util
        import sys
        # Ensure local directories are in search path
        for path in (".", "src", "src/skills"):
            if path not in sys.path:
                sys.path.insert(0, path)
        for alias in node.names:
            name = alias.name.split('.')[0]
            if name in ("moskv_1", "sortu_apex_forge", "redteam_auditor", "exergy_sensor"):
                continue
            try:
                spec = importlib.util.find_spec(name)
                if spec is None:
                    self.score -= 0.5
                    self.violations.append(f"Module '{name}' is not installed in the active environment (-0.5)")
            except Exception:
                self.score -= 0.5
                self.violations.append(f"Module '{name}' failed validation (-0.5)")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        import importlib.util
        import sys
        for path in (".", "src", "src/skills"):
            if path not in sys.path:
                sys.path.insert(0, path)
        if node.level == 0 and node.module:
            name = node.module.split('.')[0]
            if name not in ("moskv_1", "sortu_apex_forge", "redteam_auditor", "exergy_sensor"):
                try:
                    spec = importlib.util.find_spec(name)
                    if spec is None:
                        self.score -= 0.5
                        self.violations.append(f"Module '{name}' is not installed in the active environment (-0.5)")
                except Exception:
                    self.score -= 0.5
                    self.violations.append(f"Module '{name}' failed validation (-0.5)")
        self.generic_visit(node)


class RedTeamCrucible:
    """The final checkpoint before a forged agent is allowed into the Ledger."""
    
    MINIMUM_YIELD = 0.85

    def __init__(self, target_dir="src/skills"):
        self.target_dir = target_dir

    def audit_swarm(self):
        print("[RED-TEAM] Initiating Hostile AST Audit on Forged Subagents...")
        search_pattern = os.path.join(self.target_dir, "*.py")
        agents = glob.glob(search_pattern)
        
        if not agents:
            print("[RED-TEAM] No agents found in the crucible.")
            return

        for agent_path in agents:
            self._execute_hostile_audit(agent_path)

    def _execute_hostile_audit(self, filepath: str):
        agent_name = os.path.basename(filepath)
        
        with open(filepath, 'r') as file:
            source = file.read()
            
        try:
            tree = ast.parse(source)
            auditor = ExergyAuditor()
            auditor.visit(tree)
            
            print(f"\\n--- AUDITING: {agent_name} ---")
            for v in auditor.violations:
                print(f"  [!] VIOLATION: {v}")
                
            print(f"  [=] FINAL EXERGY YIELD: E={auditor.score:.2f}")
            
            if auditor.score < self.MINIMUM_YIELD:
                print(f"  [X] YIELD TOO LOW. INITIATING DESTRUCTION PROTOCOL.")
                os.remove(filepath)
                print(f"  [X] {agent_name} ERASED FROM PHYSICAL SUBSTRATE.")
            else:
                print(f"  [+] AGENT VERIFIED. CLEARED FOR VESICULAR RUNTIME.")
                
        except SyntaxError:
            print(f"\\n[X] CRITICAL: {agent_name} failed base compilation. Erasing.")
            os.remove(filepath)

if __name__ == "__main__":
    crucible = RedTeamCrucible()
    crucible.audit_swarm()
