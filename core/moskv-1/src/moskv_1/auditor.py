import yaml
from dataclasses import dataclass
from typing import Optional
from kernel.event_bus import CortexEvent, EventBus

@dataclass
class AuditResult:
    passed: bool
    level: str
    reason: str

class CognitiveLevel:
    R0 = "R0_UNVERIFIED"
    R1 = "R1_STRUCTURED"
    R2 = "R2_STRUCTURAL_VALIDATION"
    R3 = "R3_LEDGER_VERIFIED"
    R4 = "R4_EXTERNAL_VERIFICATION"
    R5 = "R5_CRYPTOGRAPHIC_VERIFICATION"

class RealityAuditor:
    REQUIRED_SCHEMA = {"Claim", "Proof"}
    PROOF_REQUIRED = {"Base", "Range", "Confidence"}

    def __init__(self, event_bus: EventBus):
        self.bus = event_bus

    async def audit(self, event: CortexEvent) -> AuditResult:
        payload = event.payload
        content = payload.get("content", "")
        
        if not isinstance(content, str):
            return AuditResult(False, CognitiveLevel.R0, "Content is not string")

        try:
            if "Claim:" not in content or "Proof:" not in content:
                return AuditResult(False, CognitiveLevel.R1, "Missing Claim or Proof in content")
            
            yaml_content = content
            if "```yaml" in content:
                parts = content.split("```yaml")
                if len(parts) > 1:
                    yaml_content = parts[1].split("```")[0]
            
            parsed = yaml.safe_load(yaml_content)
            
            if not isinstance(parsed, dict):
                return AuditResult(False, CognitiveLevel.R1, "YAML parsed to non-dict")

            # Check R2 Structural Validation
            if not self.REQUIRED_SCHEMA.issubset(parsed.keys()):
                return AuditResult(False, CognitiveLevel.R1, "Missing Claim or Proof root keys")
            
            proof = parsed["Proof"]
            if not isinstance(proof, dict):
                return AuditResult(False, CognitiveLevel.R1, "Proof must be a dictionary")
                
            if not self.PROOF_REQUIRED.issubset(proof.keys()):
                return AuditResult(False, CognitiveLevel.R1, "Proof missing Base, Range, or Confidence")
            
            confidence = str(proof.get("Confidence", ""))
            if "C5" not in confidence:
                return AuditResult(False, CognitiveLevel.R2, "Confidence must be C5 for strict verification")

            base_hash = str(proof.get("Base", ""))
            is_verified = await self.bus.verify_hash_exists(base_hash)
            if not is_verified:
                return AuditResult(False, CognitiveLevel.R2, f"Causal Anchor Failed: Hash {base_hash} not in Event Ledger")
            return AuditResult(True, CognitiveLevel.R3, "Ledger Verified C5 Claim")
        except yaml.YAMLError as e:
            return AuditResult(False, CognitiveLevel.R0, f"YAML Parse Error: {str(e)}")
        except Exception as e:
            return AuditResult(False, CognitiveLevel.R0, f"Audit Execution Error: {str(e)}")
