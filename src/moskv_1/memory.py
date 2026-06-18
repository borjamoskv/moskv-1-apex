import json
import time
import asyncio
import os
from enum import Enum
from typing import Optional, Dict, Any, List
from moskv_1.event_bus import CortexEvent
from moskv_1.immunity import ImmunityLayer, ImmuneState

try:
    from neo4j import AsyncGraphDatabase
except ImportError:
    AsyncGraphDatabase = None

try:
    import lancedb
except ImportError:
    lancedb = None

class MemoryRoutingDecision(Enum):
    DISCARD = "discard"
    WORKING = "working"      # L0
    EPISODIC = "episodic"    # L1
    SEMANTIC = "semantic"    # L2
    PROCEDURAL = "procedural"  # L3
    LEDGER = "ledger"        # L4

class MemoryGovernor:
    """
    Arbitrates the cognitive retention of events across the L0-L4 Memory Stack.
    """
    def __init__(self, immunity_layer: ImmunityLayer):
        self.immunity = immunity_layer

    def evaluate(self, event: CortexEvent, entropy: float, immune_state: ImmuneState) -> MemoryRoutingDecision:
        payload = event.payload
        is_procedural = payload.get("is_procedural", False)
        is_transaction = payload.get("is_transaction", False)

        if immune_state == ImmuneState.NECROTIC:
            return MemoryRoutingDecision.DISCARD
            
        if is_transaction:
            return MemoryRoutingDecision.LEDGER
            
        if is_procedural:
            return MemoryRoutingDecision.PROCEDURAL

        if entropy > self.immunity.high_threshold:
            return MemoryRoutingDecision.SEMANTIC
        elif entropy > self.immunity.mid_threshold:
            return MemoryRoutingDecision.EPISODIC
        else:
            return MemoryRoutingDecision.WORKING


class InMemoryNode:
    def __init__(self, element_id: str, labels: list, properties: dict):
        self.element_id = element_id
        self.labels = labels
        self._properties = properties

    @property
    def id(self):
        return self.element_id

    def __getitem__(self, key):
        return self._properties[key]

    def get(self, key, default=None):
        return self._properties.get(key, default)

    def keys(self):
        return self._properties.keys()

    def values(self):
        return self._properties.values()

    def items(self):
        return self._properties.items()

class InMemoryRecord:
    def __init__(self, data: dict):
        self._data = data

    def __getitem__(self, key):
        if isinstance(key, int):
            return list(self._data.values())[key]
        return self._data[key]

    def get(self, key, default=None):
        return self._data.get(key, default)

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

class MemoryStore:
    """
    Sovereign Graph Database interface. Simulates the Neo4j API in-memory
    when no real driver is connected, but uses the Neo4j transaction context properly when driver is set.
    """
    def __init__(self, uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "password", data_dir: str = ".moskv_data"):
        self.uri = uri
        self.user = user
        self.password = password
        self.data_dir = data_dir
        self.driver: Any = None
        self._nodes: Dict[str, Dict[str, Any]] = {}
        self._regions: Dict[str, Dict[str, Any]] = {}
        self._relationships: List[tuple] = []
        self.immunity = ImmunityLayer()
        self.governor = MemoryGovernor(self.immunity)
        self._pruning_in_progress = False
        self.lancedb_db = None
        self.l1_table = None
        
        # Ensure data dir exists for L1 and L4
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        self.ledger_path = os.path.join(self.data_dir, "l4_ledger.ndjson")

    async def connect(self):
        """
        Connects to the Neo4j instance if the library is available, or defaults to in-memory mode.
        """
        if AsyncGraphDatabase is not None:
            try:
                self.driver = AsyncGraphDatabase.driver(
                    self.uri,
                    auth=(self.user, self.password),
                    max_connection_pool_size=50,
                    connection_acquisition_timeout=20.0,
                    connection_timeout=5.0,
                    max_transaction_retry_time=5.0
                )
                await self.driver.verify_connectivity()
                # Create unique constraint on MemoryNode(id) to optimize MERGE queries
                async def init_schema(tx):
                    await tx.run("CREATE CONSTRAINT memory_node_id IF NOT EXISTS FOR (n:MemoryNode) REQUIRE n.id IS UNIQUE")
                async with self.driver.session() as session:
                    await session.execute_write(init_schema)
                print("[MemoryStore] Neo4j Driver connected. Graph mutation active and constraint initialized.")
                return
            except Exception as e:
                print(f"[MemoryStore] Failed to connect to Neo4j: {e}")
                raise e
        print("[MemoryStore] Using in-memory mode (Neo4j driver not available).")
        
        if lancedb is not None:
            try:
                self.lancedb_db = lancedb.connect(os.path.join(self.data_dir, "lancedb"))
                print("[MemoryStore] LanceDB (L1_Episodic) initialized.")
            except Exception as e:
                print(f"[MemoryStore] Failed to connect to LanceDB: {e}")

    async def crystallize(self, event: CortexEvent) -> List[Any]:
        """
        Creates/updates a MemoryNode from a CortexEvent structure and links it to its BrainRegion.
        Also evaluates the signal using the Immunity Layer.
        """
        payload = event.payload
        source_region = payload.get("sourceRegion", "Unknown")
        entropy = payload.get("entropy")
        content = payload.get("content", "Void")

        if isinstance(content, (dict, list)):
            content_str = json.dumps(content)
        else:
            content_str = str(content)

        # Evaluate via Immunity Layer if is_quarantined is not explicitly passed
        immune_state_obj, calculated_entropy = self.immunity.evaluate_signal(content_str)
        if entropy is None:
            entropy = calculated_entropy
        
        is_quarantined = payload.get("is_quarantined")
        if is_quarantined is None:
            is_quarantined = (immune_state_obj == ImmuneState.QUARANTINED or immune_state_obj == ImmuneState.NECROTIC)
            
        immune_state = payload.get("immune_state", immune_state_obj.value)

        node_id = payload.get("nodeId") or event.hash

        routing_decision = self.governor.evaluate(event, entropy, immune_state_obj)
        
        if routing_decision == MemoryRoutingDecision.DISCARD:
            return []
            
        if routing_decision == MemoryRoutingDecision.LEDGER:
            try:
                with open(self.ledger_path, "a") as f:
                    f.write(json.dumps({"hash": event.hash, "timestamp": time.time(), "payload": payload}) + "\n")
            except Exception as e:
                print(f"[MemoryStore] Failed to write to Ledger: {e}")
            return []

        if routing_decision == MemoryRoutingDecision.EPISODIC and self.lancedb_db is not None:
            try:
                data = [{"id": node_id, "vector": [0.0]*128, "content": content_str, "entropy": float(entropy)}]
                if self.l1_table is None:
                    if "episodic" in self.lancedb_db.table_names():
                        self.l1_table = self.lancedb_db.open_table("episodic")
                        self.l1_table.add(data)
                    else:
                        self.l1_table = self.lancedb_db.create_table("episodic", data=data)
                else:
                    self.l1_table.add(data)
            except Exception as e:
                print(f"[MemoryStore] LanceDB L1 routing error: {e}")

        if entropy > self.immunity.high_threshold * 1.5:
            if not self._pruning_in_progress:
                self._pruning_in_progress = True
                print("[MemoryStore] Event-Driven Apoptosis Triggered due to high entropy spike.")
                
                async def run_prune_task():
                    try:
                        await self.prune(self.immunity.high_threshold)
                    finally:
                        self._pruning_in_progress = False
                
                asyncio.create_task(run_prune_task())

        if self.driver and routing_decision in (MemoryRoutingDecision.SEMANTIC, MemoryRoutingDecision.WORKING, MemoryRoutingDecision.PROCEDURAL):
            cypher = """
                MERGE (r:BrainRegion {name: $sourceRegion})
                MERGE (n:MemoryNode {id: $id}) 
                SET n.entropy = $entropy, 
                    n.content = $content, 
                    n.lastUpdated = timestamp(),
                    n.spawnHash = $hash,
                    n.is_quarantined = $is_quarantined,
                    n.immune_state = $immune_state
                MERGE (n)-[:SYNTHESIZED_BY]->(r)
                RETURN n
            """
            async def work(tx):
                res = await tx.run(
                    cypher,
                    id=node_id,
                    entropy=entropy,
                    content=content_str,
                    sourceRegion=source_region,
                    hash=event.hash,
                    is_quarantined=is_quarantined,
                    immune_state=immune_state
                )
                # Consume and materialize results INSIDE transaction callback
                return [record async for record in res]

            async with self.driver.session() as session:
                records = await session.execute_write(work)
                return records
        else:
            # In-memory graph store crystallization
            self._regions[source_region] = {"name": source_region}
            now_ms = time.time() * 1000.0
            node_props = {
                "id": node_id,
                "entropy": entropy,
                "content": content_str,
                "lastUpdated": now_ms,
                "spawnHash": event.hash,
                "sourceRegion": source_region,
                "is_quarantined": is_quarantined,
                "immune_state": immune_state
            }
            self._nodes[node_id] = node_props
            rel = (node_id, "SYNTHESIZED_BY", source_region)
            if rel not in self._relationships:
                self._relationships.append(rel)

            node_obj = InMemoryNode(element_id=node_id, labels=["MemoryNode"], properties=node_props)
            record = InMemoryRecord({"n": node_obj})
            return [record]

    async def quarantine(self, node_id: str, reason: str) -> bool:
        """Manually put a memory node into quarantine status."""
        if self.driver:
            cypher = """
                MATCH (n:MemoryNode {id: $id})
                SET n.is_quarantined = true,
                    n.quarantine_reason = $reason,
                    n.immune_state = "quarantined"
                RETURN n
            """
            async def work(tx):
                res = await tx.run(cypher, id=node_id, reason=reason)
                return [record async for record in res]
            async with self.driver.session() as session:
                records = await session.execute_write(work)
                return len(records) > 0
        else:
            if node_id in self._nodes:
                self._nodes[node_id]["is_quarantined"] = True
                self._nodes[node_id]["quarantine_reason"] = reason
                self._nodes[node_id]["immune_state"] = "quarantined"
                return True
            return False

    async def unquarantine(self, node_id: str) -> bool:
        """Lift quarantine status from a memory node."""
        if self.driver:
            cypher = """
                MATCH (n:MemoryNode {id: $id})
                SET n.is_quarantined = false,
                    n.immune_state = "promotable"
                REMOVE n.quarantine_reason
                RETURN n
            """
            async def work(tx):
                res = await tx.run(cypher, id=node_id)
                return [record async for record in res]
            async with self.driver.session() as session:
                records = await session.execute_write(work)
                return len(records) > 0
        else:
            if node_id in self._nodes:
                self._nodes[node_id]["is_quarantined"] = False
                self._nodes[node_id]["immune_state"] = "promotable"
                self._nodes[node_id].pop("quarantine_reason", None)
                return True
            return False

    async def prune(self, entropy_threshold: float) -> int:
        """
        Purges memory nodes with entropy higher than the threshold that haven't crystallized (older than 24 hours).
        """
        if self.driver:
            cypher = """
                MATCH (n:MemoryNode)
                WHERE n.entropy > $threshold AND n.lastUpdated < (timestamp() - 86400000)
                DETACH DELETE n
                RETURN count(n) as pruned
            """
            async def work(tx):
                res = await tx.run(cypher, threshold=entropy_threshold)
                record = await res.single()
                return record["pruned"] if record else 0

            async with self.driver.session() as session:
                pruned_count = await session.execute_write(work)
                print(f"[MemoryStore] Pruned {pruned_count} high-entropy nodes.")
                return pruned_count
        else:
            now_ms = time.time() * 1000.0
            cutoff = now_ms - 86400000.0  # 24 hours in ms
            to_prune = []
            for node_id, props in list(self._nodes.items()):
                if props["entropy"] > entropy_threshold and props["lastUpdated"] < cutoff:
                    to_prune.append(node_id)

            for node_id in to_prune:
                if node_id in self._nodes:
                    del self._nodes[node_id]
                self._relationships = [r for r in self._relationships if r[0] != node_id]

            pruned_count = len(to_prune)
            print(f"[MemoryStore] Pruned {pruned_count} high-entropy nodes (in-memory).")
            return pruned_count

    async def close(self):
        """
        Closes the Neo4j driver connection.
        """
        if self.driver:
            await self.driver.close()
            print("[MemoryStore] Neo4j Connection Closed.")
        else:
            print("[MemoryStore] In-memory Connection Closed.")
