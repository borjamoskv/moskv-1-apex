import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from moskv_1.event_bus import EventBus, CortexEvent

def test_cortex_event_serialization():
    event = CortexEvent(
        hash="hash123",
        prev_hash="prev123",
        timestamp=1234567890.0,
        payload={"data": "test"}
    )
    json_str = event.to_json()
    decoded = CortexEvent.from_json(json_str)
    assert decoded.hash == event.hash
    assert decoded.prev_hash == event.prev_hash
    assert decoded.timestamp == event.timestamp
    assert decoded.payload == event.payload

def test_event_bus_hash_chaining():
    bus = EventBus()
    # Initial state
    assert bus.last_hash == "GENESIS"
    
    # First hash
    p1 = {"step": 1}
    h1 = bus._hash(p1, "GENESIS")
    assert h1 is not None
    
    # Second hash depends on first hash
    p2 = {"step": 2}
    h2 = bus._hash(p2, h1)
    assert h2 is not None
    assert h1 != h2

@pytest.mark.asyncio
async def test_event_bus_publish_mocked():
    bus = EventBus()
    bus.js = AsyncMock()  # Mock NATS JetStream Context
    
    payload = {"value": 42}
    event = await bus.publish("cortex.test", payload)
    
    assert event.payload == payload
    assert event.prev_hash == "GENESIS"
    assert event.hash == bus._hash(payload, "GENESIS")
    assert bus.last_hash == event.hash
    bus.js.publish.assert_called_once()

@pytest.mark.asyncio
async def test_event_bus_connect_mocked():
    bus = EventBus()
    mock_nc = MagicMock()
    mock_nc.drain = AsyncMock()
    mock_nc.close = AsyncMock()
    mock_js = AsyncMock()
    mock_nc.jetstream = MagicMock(return_value=mock_js)
    
    with patch("nats.connect", new_callable=AsyncMock, return_value=mock_nc) as mock_connect:
        await bus.connect()
        mock_connect.assert_called_once_with("nats://localhost:4222", max_reconnect_attempts=-1)
        mock_js.add_stream.assert_called_once()
        assert bus.nc == mock_nc
        assert bus.js == mock_js

@pytest.mark.asyncio
async def test_event_bus_subscribe_mocked():
    bus = EventBus()
    mock_js = AsyncMock()
    bus.js = mock_js
    
    async def dummy_callback(event, msg):
        pass
        
    await bus.subscribe("cortex.test", dummy_callback, "durable_test")
    mock_js.subscribe.assert_called_once()

@pytest.mark.asyncio
async def test_event_bus_close_mocked():
    bus = EventBus()
    mock_nc = AsyncMock()
    bus.nc = mock_nc
    
    await bus.close()
    mock_nc.drain.assert_called_once()
    mock_nc.close.assert_called_once()
