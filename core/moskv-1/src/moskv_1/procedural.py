import ast
import json
import time
from typing import Optional, Dict, Any, List

class ProceduralStore:
    """
    L3 Procedural Memory Engine.
    Manages autonomous extraction, crystallization, and retrieval of execution scripts and AST skills.
    Maintains a strictly isolated procedural latent space to avoid polluting Episodic/Semantic graphs.
    """
    def __init__(self, lancedb_db=None, neo4j_driver=None):
        self.lancedb_db = lancedb_db
        self.neo4j_driver = neo4j_driver
        self.table_name = "procedural_skills"
        self.l3_table = None
        self._init_lancedb()

    def _init_lancedb(self):
        if self.lancedb_db is not None:
            try:
                # Dummy vector for schema init
                data = [{"id": "init_skill", "vector": [0.0]*128, "name": "init", "code": "pass", "intent": "init"}]
                if self.table_name in self.lancedb_db.table_names():
                    self.l3_table = self.lancedb_db.open_table(self.table_name)
                else:
                    self.l3_table = self.lancedb_db.create_table(self.table_name, data=data)
                print("[ProceduralStore] LanceDB (L3_Procedural) isolated table initialized.")
            except Exception as e:
                print(f"[ProceduralStore] Failed to init procedural table: {e}")

    def extract_ast_routine(self, file_path: str, func_name: str) -> Optional[str]:
        """
        Parses a C5-REAL source file and returns the exact AST source code for the requested function.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if node.name == func_name:
                        return ast.get_source_segment(source, node)
        except Exception as e:
            print(f"[ProceduralStore] AST Extraction Error: {e}")
        return None

    def crystallize_skill(self, name: str, code: str, intent: str, node_id: str = None) -> bool:
        """
        Crystallizes the AST code into the L3 Vector and Graph databases.
        """
        if not node_id:
            node_id = f"skill_{int(time.time() * 1000)}"

        # 1. LanceDB (Semantic Space)
        if self.l3_table is not None:
            try:
                # In a real environment, vector would be calculated via an embedding model
                dummy_vector = [0.01] * 128
                data = [{"id": node_id, "vector": dummy_vector, "name": name, "code": code, "intent": intent}]
                self.l3_table.add(data)
            except Exception as e:
                print(f"[ProceduralStore] Failed to insert skill in LanceDB: {e}")
                return False

        # 2. Neo4j (Topological Space)
        if self.neo4j_driver is not None:
            cypher = """
                MERGE (n:ProceduralSkill {id: $id})
                SET n.name = $name,
                    n.intent = $intent,
                    n.crystallized_at = timestamp()
            """
            try:
                with self.neo4j_driver.session() as session:
                    session.run(cypher, id=node_id, name=name, intent=intent)
            except Exception as e:
                print(f"[ProceduralStore] Failed to insert skill in Neo4j: {e}")
                return False

        return True

    def retrieve_closest_skill(self, intent_query: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves the most semantically relevant AST code.
        """
        if self.l3_table is not None:
            try:
                # Mock embedding lookup
                dummy_query_vector = [0.01] * 128
                results = self.l3_table.search(dummy_query_vector).limit(1).to_pandas()
                if not results.empty:
                    row = results.iloc[0]
                    # Don't return the dummy init
                    if row["id"] != "init_skill":
                        return {
                            "id": row["id"],
                            "name": row["name"],
                            "code": row["code"],
                            "intent": row["intent"]
                        }
            except Exception as e:
                print(f"[ProceduralStore] Failed to retrieve skill: {e}")
        return None
