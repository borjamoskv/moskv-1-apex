import json
from typing import Optional, Union, Dict, Any
from neo4j import AsyncGraphDatabase
from moskv_1.event_bus import CortexEvent

class MemoryStore:
    """
    Sovereign Graph Database interface (Neo4j) representing the crystallized neural memory of the swarm.
    """
    def __init__(self, uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "password"):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None

    async def connect(self):
        """
        Connects to the Neo4j instance and verifies connectivity.
        """
        try:
            self.driver = AsyncGraphDatabase.driver(
                self.uri, 
                auth=(self.user, self.password),
                max_connection_pool_size=50,
                connection_acquisition_timeout=20.0
            )
            await self.driver.verify_connectivity()
            print("[MemoryStore] Neo4j Driver connected. Graph mutation active.")
        except Exception as e:
            print(f"[MemoryStore] Failed to connect to Neo4j: {e}")
            raise e

    async def crystallize(self, event: CortexEvent) -> Dict[str, Any]:
        """
        Creates/updates a MemoryNode from a CortexEvent structure and links it to its BrainRegion.
        """
        if not self.driver:
            raise RuntimeError("MemoryStore is not connected. Call connect() first.")

        payload = event.payload
        source_region = payload.get("sourceRegion", "Unknown")
        entropy = payload.get("entropy", 1.0)
        content = payload.get("content", "Void")

        if isinstance(content, (dict, list)):
            content_str = json.dumps(content)
        else:
            content_str = str(content)

        cypher = """
            MERGE (r:BrainRegion {name: $sourceRegion})
            MERGE (n:MemoryNode {id: $id}) 
            SET n.entropy = $entropy, 
                n.content = $content, 
                n.lastUpdated = timestamp(),
                n.spawnHash = $hash
            MERGE (n)-[:SYNTHESIZED_BY]->(r)
            RETURN n
        """

        async with self.driver.session() as session:
            result = await session.execute_write(
                lambda tx: tx.run(
                    cypher,
                    id=payload.get("nodeId") or event.hash,
                    entropy=entropy,
                    content=content_str,
                    sourceRegion=source_region,
                    hash=event.hash
                )
            )
            # Retrieve records (useful for verifying or return)
            records = [record async for record in result]
            return records

    async def prune(self, entropy_threshold: float) -> int:
        """
        Purges memory nodes with entropy higher than the threshold that haven't crystallized (older than 60s).
        """
        if not self.driver:
            raise RuntimeError("MemoryStore is not connected. Call connect() first.")

        cypher = """
            MATCH (n:MemoryNode)
            WHERE n.entropy > $threshold AND n.lastUpdated < (timestamp() - 60000)
            DETACH DELETE n
            RETURN count(n) as pruned
        """

        async with self.driver.session() as session:
            result = await session.execute_write(
                lambda tx: tx.run(cypher, threshold=entropy_threshold)
            )
            record = await result.single()
            pruned_count = record["pruned"] if record else 0
            print(f"[MemoryStore] Pruned {pruned_count} high-entropy nodes.")
            return pruned_count

    async def close(self):
        """
        Closes the Neo4j driver connection.
        """
        if self.driver:
            await self.driver.close()
            print("[MemoryStore] Neo4j Connection Closed.")
