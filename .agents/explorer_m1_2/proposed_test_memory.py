import pytest
from unittest.mock import AsyncMock, MagicMock
from moskv_1.memory import MemoryStore
from moskv_1.event_bus import CortexEvent

@pytest.mark.asyncio
async def test_memory_store_crystallize_mocked():
    store = MemoryStore()
    
    # Mock Neo4j driver and session
    mock_session = AsyncMock()
    mock_driver = MagicMock()
    mock_driver.session = MagicMock(return_value=mock_session)
    store.driver = mock_driver
    
    event = CortexEvent(
        hash="eventhash123",
        prev_hash="genesis",
        timestamp=1000.0,
        payload={"sourceRegion": "Reasoning", "entropy": 0.95, "content": "Visual anomaly"}
    )
    
    await store.crystallize(event)
    
    mock_session.execute_write.assert_called_once()

@pytest.mark.asyncio
async def test_memory_store_prune_mocked():
    store = MemoryStore()
    
    # Mock Neo4j session and driver
    mock_session = AsyncMock()
    mock_driver = MagicMock()
    mock_driver.session = MagicMock(return_value=mock_session)
    store.driver = mock_driver
    
    # Mock returned pruned count
    mock_result = AsyncMock()
    mock_result.single = AsyncMock(return_value={"pruned": 5})
    mock_session.execute_write.return_value = mock_result
    
    pruned_count = await store.prune(0.90)
    
    assert pruned_count == 5
    mock_session.execute_write.assert_called_once()
