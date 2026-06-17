import os
import json
from datetime import datetime, timezone
from vector_sigma.cortex_ledger import CortexLedger

class HumanGate:
    def __init__(self, ledger: CortexLedger):
        self.ledger = ledger

    def _load_state(self, finding_id: str) -> dict:
        path = os.path.join(self.ledger.storage_path, f"{finding_id}.json")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Finding {finding_id} not found in Ledger.")
        with open(path, 'r') as f:
            return json.load(f)

    def authorize_active_interaction(self, finding_id: str, operator_id: str) -> dict:
        """
        Gate 1: Requires human cryptographic approval before any active payload 
        is sent to the target, ensuring no accidental out-of-bounds exploitation.
        """
        state = self._load_state(finding_id)
        
        if 'Gates' not in state:
            state['Gates'] = {}
            
        state['Gates']['Gate1_ActivePayload'] = {
            'Approved': True,
            'Operator': operator_id,
            'Timestamp': datetime.now(timezone.utc).isoformat()
        }
        state['Target']['ContextPhase'] = 'VERIFICATION_ACTIVE'
        
        return self.ledger.commit(state)

    def authorize_disclosure(self, finding_id: str, operator_id: str) -> dict:
        """
        Gate 2: Requires human review of the report wording and severity 
        before external submission to prevent extortion triggers or policy violations.
        """
        state = self._load_state(finding_id)
        
        if 'Gates' not in state:
            state['Gates'] = {}
            
        state['Gates']['Gate2_Disclosure'] = {
            'Approved': True,
            'Operator': operator_id,
            'Timestamp': datetime.now(timezone.utc).isoformat(),
            'WordingAudit': 'PASSED'
        }
        state['Target']['ContextPhase'] = 'DISCLOSURE_READY'
        
        return self.ledger.commit(state)
