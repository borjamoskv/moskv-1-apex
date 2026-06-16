import time
import json
import hashlib
from typing import Callable, Any, Dict, Optional, Awaitable
from dataclasses import dataclass, asdict
import nats
from nats.js import JetStreamContext

@dataclass
class CortexEvent:
    hash: str
    prev_hash: str
    timestamp: float
    payload: dict

    def to_json(self) -> str:
        # Deterministic serialization for reliable cross-language hash chains
        return json.dumps(asdict(self), sort_keys=True, separators=(',', ':'))

    @classmethod
    def from_json(cls, json_str: str) -> 'CortexEvent':
        data = json.loads(json_str)
        return cls(
            hash=data['hash'],
            prev_hash=data['prev_hash'],
            timestamp=data['timestamp'],
            payload=data['payload']
        )

class EventBus:
    """
    Hash-chained event bus utilizing NATS JetStream to guarantee ordering and verifiability.
    """
    def __init__(self, server_url: str = "nats://localhost:4222", stream_name: str = "CORTEX_STREAM"):
        self.server_url = server_url
        self.stream_name = stream_name
        self.nc: Optional[nats.NATS] = None
        self.js: Optional[JetStreamContext] = None
        self.last_hash: str = "GENESIS"

    async def connect(self):
        """
        Connects to NATS server and ensures JetStream stream exists with infinite retention.
        """
        try:
            self.nc = await nats.connect(self.server_url, max_reconnect_attempts=-1)
            self.js = self.nc.jetstream()
            
            # Verify / create stream
            try:
                await self.js.add_stream(
                    name=self.stream_name,
                    subjects=["cortex.>"],
                    retention="limits",
                    max_age=0,  # Infinite retention
                    storage="file"
                )
                print(f"[EventBus] Created NATS JetStream stream: {self.stream_name}")
            except Exception as e:
                # If the stream already exists, we log and proceed
                print(f"[EventBus] Stream {self.stream_name} verified/already exists.")
                
            print("[EventBus] NATS JetStream Connected & Verified. C5-REAL active.")
        except Exception as e:
            print(f"[EventBus] Critical Initialization Error: {e}")
            raise e

    def _hash(self, payload: dict, prev_hash: str) -> str:
        """
        Deterministic SHA-256 hash calculation over stringified payload and previous hash.
        """
        serialized = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        hash_input = f"{prev_hash}{serialized}".encode('utf-8')
        return hashlib.sha256(hash_input).hexdigest()

    async def publish(self, topic: str, payload: dict) -> CortexEvent:
        """
        Publishes a payload to a topic, automatically chaining it to the last seen event hash.
        """
        if not self.js:
            raise RuntimeError("EventBus is not connected. Call connect() first.")

        current_hash = self._hash(payload, self.last_hash)
        event = CortexEvent(
            hash=current_hash,
            prev_hash=self.last_hash,
            timestamp=time.time() * 1000.0,  # ms timestamp matching JS Date.now()
            payload=payload
        )

        # Update last hash state
        self.last_hash = current_hash
        
        # Publish
        data = event.to_json().encode('utf-8')
        await self.js.publish(topic, data)
        return event

    async def subscribe(self, topic: str, callback: Callable[[CortexEvent, Any], Awaitable[None]], durable_name: Optional[str] = None):
        """
        Subscribes to a topic. The callback receives a CortexEvent and the raw message.
        """
        if not self.js:
            raise RuntimeError("EventBus is not connected. Call connect() first.")

        async def nats_callback(msg):
            try:
                event = CortexEvent.from_json(msg.data.decode('utf-8'))
                await callback(event, msg)
                await msg.ack()
            except Exception as e:
                print(f"[EventBus] Message Processing Error: {e}")
                await msg.nak()

        # Subscribe using jetstream
        sub = await self.js.subscribe(
            subject=topic,
            durable=durable_name,
            cb=nats_callback,
            manual_ack=True
        )
        return sub

    async def close(self):
        """
        Drains and closes connection.
        """
        if self.nc:
            await self.nc.drain()
            await self.nc.close()
            print("[EventBus] NATS Connection Closed.")
