import json
import hashlib
import hmac

class ACP_v01:
    """
    Reference Implementation of Agent Commerce Protocol v0.1.
    Stripped of all abstractions. Just math.
    """
    @staticmethod
    def canonical_json(payload: dict) -> bytes:
        # Sort keys to ensure deterministic hashing
        return json.dumps(payload, separators=(',', ':'), sort_keys=True).encode('utf-8')

    @staticmethod
    def sign_transaction(payload: dict, secret_seed: str) -> str:
        canonical = ACP_v01.canonical_json(payload)
        h1 = hashlib.sha256(canonical).digest()
        # In this reference we use HMAC-SHA256 over H1 as a surrogate for Ed25519
        signature = hmac.new(secret_seed.encode('utf-8'), h1, hashlib.sha256).hexdigest()
        return signature

    @staticmethod
    def verify_transaction(payload: dict, signature: str, secret_seed: str) -> bool:
        expected = ACP_v01.sign_transaction(payload, secret_seed)
        return hmac.compare_digest(expected, signature)

if __name__ == "__main__":
    # Test Vector 1
    tv1_payload = {
        "agent_id": "test_agent_1",
        "amount": 100,
        "currency": "USD",
        "nonce": 1234567890,
        "target_address": "acct_test"
    }
    tv1_seed = "00000000000000000000000000000000"
    
    sig = ACP_v01.sign_transaction(tv1_payload, tv1_seed)
    print(f"ACP TEST VECTOR 1 SIGNATURE: {sig}")
    
    is_valid = ACP_v01.verify_transaction(tv1_payload, sig, tv1_seed)
    assert is_valid, "Test Vector 1 failed validation"
    print("ACP TEST VECTOR 1: PASS")
