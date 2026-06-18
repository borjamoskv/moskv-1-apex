import pytest
import asyncio
from moskv_1.event_bus import CortexEvent, EventBus
from moskv_1.memory import MemoryGovernor, MemoryRoutingDecision, ImmuneState, ImmunityLayer
from moskv_1.brain import BrainRegion

@pytest.mark.asyncio
async def test_memory_governor_routing():
    immunity = ImmunityLayer()
    governor = MemoryGovernor(immunity)
    
    event_tx = CortexEvent(hash="tx123", prevHash="tx0", timestamp=100.0, payload={"is_transaction": True})
    decision = governor.evaluate(event_tx, 0.5, ImmuneState.PROMOTABLE)
    assert decision == MemoryRoutingDecision.LEDGER
    event_semantic = CortexEvent(hash="sem123", prevHash="tx0", timestamp=100.0, payload={"content": "new abstract concept"})
    decision = governor.evaluate(event_semantic, immunity.high_threshold + 0.1, ImmuneState.PROMOTABLE)
    assert decision == MemoryRoutingDecision.SEMANTIC

    event_episodic = CortexEvent(hash="ep123", prevHash="tx0", timestamp=100.0, payload={"content": "a daily thought"})
    decision = governor.evaluate(event_episodic, immunity.mid_threshold + 0.05, ImmuneState.PROMOTABLE)
    assert decision == MemoryRoutingDecision.EPISODIC
    event_working = CortexEvent(hash="wrk123", prevHash="tx0", timestamp=100.0, payload={"content": "trivial ping"})
    decision = governor.evaluate(event_working, immunity.mid_threshold - 0.1, ImmuneState.PROMOTABLE)
    assert decision == MemoryRoutingDecision.WORKING

@pytest.mark.asyncio
async def test_exergy_scheduler_priority():
    bus = EventBus(server_url="nats://localhost:4222")
    
    execution_order = []
    
    async def high_priority_task(event, msg):
        execution_order.append("high")
        
    async def low_priority_task(event, msg):
        execution_order.append("low")

    await bus.task_queue.put((-1, 1, low_priority_task, None, None))
    await bus.task_queue.put((-10000, 2, high_priority_task, None, None))
    while not bus.task_queue.empty():
        item = await bus.task_queue.get()
        await item[2](None, None)
    assert execution_order == ["high", "low"]
    
@pytest.mark.asyncio
async def test_brain_region_suspension():
    region = BrainRegion(region_name="TestRegion")
    assert not region.is_suspended
    
    region.suspend()
    assert region.is_suspended
    assert "suspended_at" in region._state_snapshot
    await region.process_event(CortexEvent(hash="123", prevHash="0", timestamp=0.0, payload={}))
    assert not region.is_suspended
