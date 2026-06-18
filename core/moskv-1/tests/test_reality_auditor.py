
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
import asyncio
from kernel.event_bus import CortexEvent, EventBus
from moskv_1.auditor import RealityAuditor, CognitiveLevel
from moskv_1.memory import MemoryStore, MemoryRoutingDecision
@pytest.fixture
def event_bus():
    bus = EventBus(server_url="nats://localhost:4222")
    bus._ledger_hashes.add("tx_valid")
    return bus
@pytest.fixture
def auditor(event_bus):
    return RealityAuditor(event_bus)
@pytest.mark.asyncio
async def test_reject_missing_claim(auditor):
    event = CortexEvent(hash="1", prevHash="0", timestamp=0.0, payload={"content": "Proof: {Base: 'tx_valid', Range: [1,1], Confidence: C5}"})
    result = await auditor.audit(event)
    assert not result.passed
    assert result.level == CognitiveLevel.R1
@pytest.mark.asyncio
async def test_reject_missing_proof(auditor):
    event = CortexEvent(hash="2", prevHash="0", timestamp=0.0, payload={"content": "Claim: Valid"})
    result = await auditor.audit(event)
    assert not result.passed
    assert result.level == CognitiveLevel.R1
@pytest.mark.asyncio
async def test_reject_invalid_proof_schema(auditor):
    content = """
    Claim: Valid
    Proof:
      Base: tx_valid
    """
    event = CortexEvent(hash="3", prevHash="0", timestamp=0.0, payload={"content": content})
    result = await auditor.audit(event)
    assert not result.passed
    assert result.level == CognitiveLevel.R1
@pytest.mark.asyncio
async def test_accept_r2_structure(auditor):
    content = """
    Claim: Valid
    Proof:
      Base: tx_valid
      Range: [1,1]
      Confidence: C5
    """
    event = CortexEvent(hash="4", prevHash="0", timestamp=0.0, payload={"content": content})
    result = await auditor.audit(event)
    assert result.passed
    assert result.level == CognitiveLevel.R3
@pytest.mark.asyncio
async def test_hash_verification_success(auditor):
    content = """
    Claim: Valid
    Proof:
      Base: tx_valid
      Range: [1,1]
      Confidence: C5
    """
    event = CortexEvent(hash="5", prevHash="0", timestamp=0.0, payload={"content": content})
    result = await auditor.audit(event)
    assert result.passed
@pytest.mark.asyncio
async def test_hash_verification_failure(auditor):
    content = """
    Claim: Valid
    Proof:
      Base: tx_invalid
      Range: [1,1]
      Confidence: C5
    """
    event = CortexEvent(hash="6", prevHash="0", timestamp=0.0, payload={"content": content})
    result = await auditor.audit(event)
    assert not result.passed
    assert result.level == CognitiveLevel.R2
@pytest.mark.asyncio
async def test_memory_promotion_requires_audit(event_bus):
    store = MemoryStore(data_dir=".test_moskv_data", event_bus=event_bus)
    content = """
    Claim: Valid
    Proof:
      Base: tx_invalid
      Range: [1,1]
      Confidence: C5
    """
    event = CortexEvent(hash="7", prevHash="0", timestamp=0.0, payload={"content": content, "entropy": 10.0})
    routing_decision = store.governor.evaluate(event, 10.0, store.immunity.evaluate_signal(content)[0])
    assert routing_decision == MemoryRoutingDecision.SEMANTIC
    assert store.auditor is not None
