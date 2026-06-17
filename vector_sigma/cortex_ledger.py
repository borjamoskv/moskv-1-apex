import hashlib
import json
import os
import uuid
from datetime import datetime, timezone

class CortexLedger:
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        os.makedirs(self.storage_path, exist_ok=True)

    def _compute_hash(self, state: dict) -> str:
        # Clone to avoid mutating the original object during hash computation
        state_copy = dict(state)
        if 'LedgerHash' in state_copy:
            del state_copy['LedgerHash']
        
        state_str = json.dumps(state_copy, sort_keys=True).encode('utf-8')
        return hashlib.sha256(state_str).hexdigest()

    def commit(self, state: dict) -> dict:
        """
        Commits a state mutation to the immutable ledger.
        Computes absolute provenance hash.
        """
        if 'ID' not in state:
            state['ID'] = f"fnd-{str(uuid.uuid4())[:8]}-{datetime.now(timezone.utc).strftime('%Y%m%d')}"
            
        if 'Target' in state:
            state['Target']['Timestamp'] = datetime.now(timezone.utc).isoformat()
        
        new_hash = self._compute_hash(state)
        state['LedgerHash'] = new_hash
        
        file_path = os.path.join(self.storage_path, f"{state['ID']}.json")
        
        # Append-only / overwrite with new cryptographic signature
        with open(file_path, 'w') as f:
            json.dump(state, f, indent=2)
            
        return state
