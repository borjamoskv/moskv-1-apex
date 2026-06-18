import ast
import time
from typing import Optional, Dict, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kernel.memory_store import get_memory_db

class ProceduralStore:
    """
    L3 Procedural Memory Engine.
    Manages autonomous extraction, crystallization, and retrieval of execution scripts and AST skills.
    Maintains a strictly isolated procedural latent space using SQLite WAL (CortexDb) - Zero heavy external dependencies.
    """
    def __init__(self, lancedb_db=None, driver=None):
        self.lancedb_db = lancedb_db
        self.driver = driver
        self._init_db()

    def _init_db(self):
        with get_memory_db() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS procedural_skills (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    intent TEXT,
                    code TEXT,
                    crystallized_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            print("[ProceduralStore] SQLite WAL (L3_Procedural) isolated table initialized.")

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
        Crystallizes the AST code into the L3 database.
        """
        if not node_id:
            node_id = f"skill_{int(time.time() * 1000)}"

        try:
            with get_memory_db() as conn:
                conn.execute("""
                    INSERT INTO procedural_skills (id, name, intent, code)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        name=excluded.name,
                        intent=excluded.intent,
                        code=excluded.code,
                        crystallized_at=CURRENT_TIMESTAMP
                """, (node_id, name, intent, code))
                conn.commit()
            return True
        except Exception as e:
            print(f"[ProceduralStore] Failed to insert skill in DB: {e}")
            return False

    def retrieve_closest_skill(self, intent_query: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves the most semantically relevant AST code (using exact text match fallback for lightweight operation).
        """
        try:
            with get_memory_db() as conn:
                cursor = conn.execute("""
                    SELECT id, name, intent, code 
                    FROM procedural_skills 
                    WHERE intent LIKE ? 
                    ORDER BY crystallized_at DESC LIMIT 1
                """, (f"%{intent_query}%",))
                row = cursor.fetchone()
                if row:
                    return dict(row)
        except Exception as e:
            print(f"[ProceduralStore] Failed to retrieve skill: {e}")
        return None
