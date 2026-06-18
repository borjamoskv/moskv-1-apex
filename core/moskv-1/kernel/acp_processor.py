import json
import time
import hmac
import hashlib
from typing import Dict, Any

class ACPValidator:
    """
    Agent Commerce Protocol (ACP v0.1) Validator
    Axiom: acp_payload is processor-agnostic. No UI, no narrative. Cryptographic state to wire.
    """
    def __init__(self, authorized_keys: Dict[str, bytes]):
        # agent_id -> secret_key mapping for HMAC (simulating Ed25519 for built-in constraints)
        self.authorized_keys = authorized_keys
        self.seen_nonces = set()

    def _canonicalize(self, payload: Dict[str, Any]) -> bytes:
        """JSON canonicalization (sorted keys)"""
        # Ensure 'sig' is removed before canonicalization
        clean_payload = {k: v for k, v in payload.items() if k != 'sig'}
        return json.dumps(clean_payload, sort_keys=True, separators=(',', ':')).encode('utf-8')

    def validate_payload(self, payload: Dict[str, Any]) -> bool:
        """
        Hard Constraints:
        - Zero Retries: Signature mismatch or nonce collision = Exception (Drop)
        - Dependency: Local validation only.
        """
        agent_id = payload.get('agent_id')
        if not agent_id or agent_id not in self.authorized_keys:
            raise ValueError("ACP-DROP: Unknown Agent")

        nonce = payload.get('nonce')
        if not nonce or nonce in self.seen_nonces:
            raise ValueError("ACP-DROP: Nonce Collision")

        # Validate freshness (e.g. within 60s)
        if abs(time.time() - nonce) > 60:
            raise ValueError("ACP-DROP: Nonce Expired")

        provided_sig = payload.get('sig')
        if not provided_sig:
            raise ValueError("ACP-DROP: Missing Signature")

        # Verify signature
        canonical = self._canonicalize(payload)
        expected_sig = hmac.new(self.authorized_keys[agent_id], canonical, hashlib.sha256).hexdigest()

        if not hmac.compare_digest(provided_sig, expected_sig):
            raise ValueError("ACP-DROP: Cryptographic Mismatch")

        self.seen_nonces.add(nonce)
        return True

    def dispatch(self, payload: Dict[str, Any]):
        """Dispatches to processor after strict validation."""
        self.validate_payload(payload)
        proc_id = payload.get('processor_id')
        amount = payload.get('amount_unit')
        target = payload.get('target')
        
        if proc_id == 'stripe_fiat':
            return self._dispatch_stripe(target, amount)
        elif proc_id == 'usdc_base':
            return self._dispatch_web3(target, amount)
        elif proc_id == 'sepa_iban':
            return self._dispatch_sepa(target, amount)
        else:
            raise ValueError(f"ACP-DROP: Unsupported Processor {proc_id}")

    def _dispatch_stripe(self, target: str, amount: int):
        # Stub for Stripe Connect integration
        return {"status": "dispatched", "processor": "stripe_fiat", "target": target, "amount": amount}

    def _dispatch_web3(self, target: str, amount: int):
        # Stub for USDC Base integration
        return {"status": "dispatched", "processor": "usdc_base", "target": target, "amount": amount}

    def _dispatch_sepa(self, target: str, amount: int):
        # Stub for SEPA IBAN B2B integration
        return {"status": "dispatched", "processor": "sepa_iban", "target": target, "amount": amount}
