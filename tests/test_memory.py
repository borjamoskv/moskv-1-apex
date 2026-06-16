import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from moskv_1.memory import MemoryStore
from moskv_1.event_bus import CortexEvent

@pytest.mark.asyncio
async def test_memory_store_connect_mocked():
    store = MemoryStore()
    mock_driver = AsyncMock()
    
    with patch("moskv_1.memory.AsyncGraphDatabase") as mock_db_class:
        mock_db_class.driver.return_value = mock_driver
        await store.connect()
        mock_db_class.driver.assert_called_once_with(
            "bolt://localhost:7687",
            auth=("neo4j", "password"),
            max_connection_pool_size=50,
            connection_acquisition_timeout=20.0
        )
        mock_driver.verify_connectivity.assert_called_once()
        assert store.driver == mock_driver

@pytest.mark.asyncio
async def test_memory_store_crystallize_mocked():
    store = MemoryStore()
    
    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = mock_session
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
    
    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = mock_session
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

@pytest.mark.asyncio
async def test_memory_store_close_mocked():
    store = MemoryStore()
    mock_driver = AsyncMock()
    store.driver = mock_driver
    
    await store.close()
    mock_driver.close.assert_called_once()
