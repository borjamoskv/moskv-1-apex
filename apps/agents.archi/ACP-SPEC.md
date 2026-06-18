# ACP v0.1 (Agent Commerce Protocol)

**Axiom:** `acp_payload` is processor-agnostic. No UI, no narrative. Cryptographic state to wire.

## 1. Supported Processors (M12-A)
1. `stripe_fiat`: Stripe Connect (B2C/B2B CC). Target: `acct_...`
2. `usdc_base`: Web3/USDC on Base. Target: `0x...`
3. `sepa_iban`: Traditional B2B. Target: `IBAN...`

## 2. Structural Invariant
JSON canonicalization (sorted keys) -> SHA-256 -> Ed25519.

```json
{
  "agent_id": "moskv_core_1",
  "amount_unit": 5000000, 
  "nonce": 1718690000,
  "processor_id": "stripe_fiat|usdc_base|sepa_iban",
  "target": "acct_xyz",
  "sig": "ed25519:..."
}
```

## 3. Hard Constraints
- **Zero Retries:** Signature mismatch or nonce collision = TCP Drop.
- **Dependency:** No external HTTP calls during validation except processor dispatch.
