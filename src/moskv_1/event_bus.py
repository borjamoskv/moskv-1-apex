import time
import json
import hashlib
import asyncio
from typing import Callable, Any, Dict, Optional, Awaitable, List
from dataclasses import dataclass, asdict, field
from moskv_1.exergy import ExergyMeter

@dataclass
class CortexEvent:
    hash: str
    prevHash: str  # camelCase key for cross-language compatibility
    timestamp: float
    payload: dict

    def to_json(self) -> str:
        # Serializes with separators and preserves key order (no sorting)
        return json.dumps(asdict(self), separators=(',', ':'))

    @classmethod
    def from_json(cls, json_str: str) -> 'CortexEvent':
        data = json.loads(json_str)
        return cls(
            hash=data['hash'],
            prevHash=data['prevHash'],
            timestamp=data['timestamp'],
            payload=data['payload']
        )

class MockMsg:
    def __init__(self, data: bytes):
        self.data = data
    async def ack(self):
        pass
    async def nak(self):
        pass

class MockSubscription:
    def __init__(self, bus: 'EventBus', topic: str, callback: Callable[[CortexEvent, Any], Awaitable[None]]):
        self.bus = bus
        self.topic = topic
        self.callback = callback

    async def unsubscribe(self):
        if self.topic in self.bus._subscriptions:
            if self.callback in self.bus._subscriptions[self.topic]:
                self.bus._subscriptions[self.topic].remove(self.callback)

def _topic_matches(subscription_topic: str, actual_topic: str) -> bool:
    """
    Standard NATS-style wildcard matching:
    - * matches any token in a topic at that level.
    - > matches any token at this level or below.
    """
    sub_parts = subscription_topic.split('.')
    act_parts = actual_topic.split('.')
    for i, sub_part in enumerate(sub_parts):
        if sub_part == '>':
            return True
        if i >= len(act_parts):
            return False
        if sub_part == '*':
            continue
        if sub_part != act_parts[i]:
            return False
    return len(sub_parts) == len(act_parts)

class EventBus:
    """
    Hash-chained in-memory event bus utilizing Python standard library.
    """
    def __init__(self, server_url: str = "nats://localhost:4222", stream_name: str = "CORTEX_STREAM"):
        self.server_url = server_url
        self.stream_name = stream_name
        self.last_hash: str = "GENESIS"
        self._subscriptions: Dict[str, List[Callable[[CortexEvent, Any], Awaitable[None]]]] = {}
        self._lock = asyncio.Lock()
        self.nc: Any = None
        self.js: Any = None
        self.task_queue = asyncio.PriorityQueue()
        self._scheduler_task = None
        self._ledger_hashes = set()
        self._ledger_hashes.add("GENESIS")
        self.exergy_meter = ExergyMeter()

    async def _exergy_scheduler_worker(self):
        while True:
            try:
                priority, task_time, callback, event, msg = await self.task_queue.get()
                try:
                    await callback(event, msg)
                except Exception as e:
                    print(f"[ExergyScheduler] Task execution failed: {e}")
                finally:
                    self.task_queue.task_done()
            except asyncio.CancelledError:
                break

    async def connect(self):
        """
        Simulates connection and ensures compatibility.
        """
        if self._scheduler_task is None:
            self._scheduler_task = asyncio.create_task(self._exergy_scheduler_worker())
        print("[EventBus] In-memory standard library EventBus Connected. C5-REAL active.")

    async def verify_hash_exists(self, target_hash: str) -> bool:
        """
        O(1) verification that a hash exists in the L0 Event Ledger.
        Used by RealityAuditor to anchor claims to true historical events.
        """
        return target_hash in self._ledger_hashes

    def _hash(self, payload: dict, prev_hash: str) -> str:
        """
        Deterministic SHA-256 hash calculation over stringified payload and previous hash.
        Payload is hashed WITHOUT key sorting.
        """
        serialized = json.dumps(payload, separators=(',', ':'))
        hash_input = f"{prev_hash}{serialized}".encode('utf-8')
        return hashlib.sha256(hash_input).hexdigest()

    async def publish(self, topic: str, payload: dict) -> CortexEvent:
        """
        Publishes a payload to a topic, automatically chaining it to the last seen event hash.
        Guarantees safety under concurrency and prevents gaps on publish failures.
        """
        async with self._lock:
            current_hash = self._hash(payload, self.last_hash)
            event = CortexEvent(
                hash=current_hash,
                prevHash=self.last_hash,
                timestamp=time.time() * 1000.0,  # ms timestamp matching JS Date.now()
                payload=payload
            )

            # Publish to NATS if mocked, or dispatch in-memory
            if self.js is not None:
                data = event.to_json().encode('utf-8')
                await self.js.publish(topic, data)
            else:
                await self._dispatch(topic, event)

            # Update last hash only after successful dispatch
            self.last_hash = current_hash
            self._ledger_hashes.add(current_hash)
            return event

    async def _dispatch(self, topic: str, event: CortexEvent):
        priority_score = self.exergy_meter.get_priority_score(event, time.time())

        for sub_topic, callbacks in self._subscriptions.items():
            if _topic_matches(sub_topic, topic):
                for cb in callbacks:
                    msg = MockMsg(event.to_json().encode('utf-8'))
                    await self.task_queue.put((priority_score, time.time(), cb, event, msg))

    async def subscribe(self, topic: str, callback: Callable[[CortexEvent, Any], Awaitable[None]], durable_name: Optional[str] = None):
        """
        Subscribes to a topic. The callback receives a CortexEvent and the raw message.
        """
        if self.js is not None:
            return await self.js.subscribe(topic, callback, durable_name)

        if topic not in self._subscriptions:
            self._subscriptions[topic] = []
        self._subscriptions[topic].append(callback)
        return MockSubscription(self, topic, callback)

    async def close(self):
        """
        Closes connection.
        """
        self._subscriptions.clear()
        print("[EventBus] In-memory EventBus closed.")
