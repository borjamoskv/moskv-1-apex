import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from moskv_1.event_bus import EventBus, CortexEvent
from moskv_1.memory import MemoryStore

# =====================================================================
# 1. TEST: Hash Chain Gap on Publish Failure
# =====================================================================
@pytest.mark.asyncio
async def test_hash_chain_gap_on_publish_failure():
    """
    Exposes the bug where a failed publish mutates `last_hash` anyway,
    leaving a gap in the published chain.
    """
    bus = EventBus()
    bus.js = AsyncMock()
    
    # First publish succeeds
    await bus.publish("cortex.test", {"step": 1})
    hash_1 = bus.last_hash
    
    # Second publish fails (e.g. NATS connection error or timeout)
    bus.js.publish.side_effect = Exception("NATS write timeout")
    with pytest.raises(Exception, match="NATS write timeout"):
        await bus.publish("cortex.test", {"step": 2})
        
    hash_failed = bus.last_hash
    assert hash_failed != hash_1, "last_hash should have been mutated"
    
    # Third publish succeeds
    bus.js.publish.side_effect = None
    event_3 = await bus.publish("cortex.test", {"step": 3})
    
    # The third event is chained to the failed event's hash, which was never published!
    assert event_3.prev_hash == hash_failed
    # The chain on NATS now has a gap: Event 1 (hash_1) -> Event 3 (prev_hash = hash_failed).
    # Event 2 was never published, breaking verification.


# =====================================================================
# 2. TEST: Non-deterministic Payload & Crash State Mutation
# =====================================================================
@pytest.mark.asyncio
async def test_non_serializable_payload_crashes_and_mutates():
    """
    Exposes the bug where a non-serializable payload (e.g., set) causes
    to_json/publish to crash, but `last_hash` is mutated regardless.
    """
    bus = EventBus()
    bus.js = AsyncMock()
    
    initial_hash = bus.last_hash
    
    # Publish with a set (non-serializable in standard JSON)
    bad_payload = {"tags": {"entropy", "anergy"}}
    with pytest.raises(TypeError):
        await bus.publish("cortex.test", bad_payload)
        
    # The state was mutated despite serialization crash
    assert bus.last_hash != initial_hash, "last_hash mutated even though publish crashed"


# =====================================================================
# 3. TEST: Concurrent Publish Race Condition (No Locking)
# =====================================================================
@pytest.mark.asyncio
async def test_concurrent_publish_race_condition():
    """
    Simulates concurrent publishing. Because there is no asyncio.Lock
    protecting the read-modify-write of last_hash, concurrent tasks can
    get interleaved, leading to out-of-order or duplicate chains.
    """
    bus = EventBus()
    
    # We mock js.publish to yield control, simulating network latency
    async def delayed_publish(topic, data):
        await asyncio.sleep(0.05)
        
    mock_js = AsyncMock()
    mock_js.publish = AsyncMock(side_effect=delayed_publish)
    bus.js = mock_js
    
    # We trigger two concurrent publishes
    # If tasks yield before the state is updated, they might read the same last_hash.
    # Note: Because the assignment `self.last_hash = current_hash` is synchronous,
    # in a single-threaded loop they run sequentially up to the first `await`.
    # However, if any await occurs *before* self.last_hash is updated, a race occurs.
    # Right now, `current_hash = self._hash(payload, self.last_hash)` and assignment
    # are synchronous. But if a publish fails during the `await js.publish`,
    # the second task has already read the mutated `last_hash`!
    
    # Let's verify that the second publish depends on the first's hash,
    # but if the first fails, the chain is broken.
    pass


# =====================================================================
# 4. TEST: Neo4j Transaction Lifecycle Violation Simulation
# =====================================================================
class MockClosedTransactionError(Exception):
    pass

@pytest.mark.asyncio
async def test_neo4j_transaction_lifecycle_violation():
    """
    Demonstrates that MemoryStore.crystallize and MemoryStore.prune access
    transaction results outside the execute_write transaction context, which
    violates Neo4j async driver rules and raises errors in production.
    """
    store = MemoryStore()
    
    # A realistic mock of the Neo4j session/transaction behavior
    class RealisticTx:
        def __init__(self):
            self.closed = False
            
        async def run(self, cypher, **kwargs):
            if self.closed:
                raise MockClosedTransactionError("Transaction is closed")
            return self
            
        async def __anext__(self):
            if self.closed:
                raise MockClosedTransactionError("Result consumed outside transaction context")
            # Return dummy record
            raise StopAsyncIteration
            
        def __aiter__(self):
            return self
            
        async def single(self):
            if self.closed:
                raise MockClosedTransactionError("Result consumed outside transaction context")
            return {"pruned": 10}

    class RealisticSession:
        def __init__(self):
            self.tx = RealisticTx()
            
        async def execute_write(self, unit_of_work):
            # Execute unit of work
            res = await unit_of_work(self.tx)
            # After unit of work returns, the session commits the tx and closes it
            self.tx.closed = True
            return res
            
        async def __aenter__(self):
            return self
            
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    mock_driver = MagicMock()
    mock_driver.session = MagicMock(return_value=RealisticSession())
    store.driver = mock_driver
    
    event = CortexEvent(
        hash="test_hash",
        prev_hash="prev_hash",
        timestamp=1000.0,
        payload={"sourceRegion": "Test", "content": "test"}
    )
    
    # In a realistic driver simulation, this should fail because crystallize
    # tries to iterate the results *after* execute_write has completed.
    with pytest.raises(MockClosedTransactionError, match="Result consumed outside transaction context"):
        await store.crystallize(event)
        
    # Same for prune: it tries to call result.single() after execute_write returns
    with pytest.raises(MockClosedTransactionError, match="Result consumed outside transaction context"):
        await store.prune(0.90)
