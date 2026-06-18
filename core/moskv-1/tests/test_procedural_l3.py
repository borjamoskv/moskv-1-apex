import pytest
import os
from moskv_1.procedural import ProceduralStore

def dummy_math_function(x, y):
    # This is a sample AST target
    return x * y + 42

@pytest.fixture
def procedural_store():
    # Provide dummy parameters since LanceDB and Neo4j are not required for AST test
    return ProceduralStore()

def test_ast_extraction(procedural_store):
    current_file = os.path.abspath(__file__)
    code = procedural_store.extract_ast_routine(current_file, "dummy_math_function")
    
    assert code is not None, "Failed to extract AST routine"
    assert "def dummy_math_function(x, y):" in code
    assert "return x * y + 42" in code

def test_crystallize_and_retrieve_fallback(procedural_store):
    # Tests that crystallization works gracefully without DBs 
    # (returns False for missing dependencies, or True if mocked).
    # Since our ProceduralStore intercepts None for databases and safely logs, it should return False
    # because the LanceDB and Neo4j drivers are missing.
    res = procedural_store.crystallize_skill("math_skill", "def foo(): pass", "do math")
    assert res is False, "Should fail crystallization if DBs are not attached"

    res_retrieve = procedural_store.retrieve_closest_skill("do math")
    assert res_retrieve is None, "Should return None if DBs are not attached"
