import pytest
from sortu_apex_forge import SwarmVector
from moskv_1.mpc_controller import CognitiveNMPC

def test_cognitive_nmpc_evaluate_template_ast() -> None:
    nmpc = CognitiveNMPC()
    valid_logic = 'print("[Test] high exergy")'
    score = nmpc.evaluate_template_ast(valid_logic)
    assert score == 1.0
    invalid_logic = 'if valid print('
    score = nmpc.evaluate_template_ast(invalid_logic)
    assert score == 0.0

def test_cognitive_nmpc_optimize_mitosis() -> None:
    nmpc = CognitiveNMPC()
    vectors = [
        SwarmVector(role="Valid Agent", logic='print("[Valid] running")', target_module="valid"),
        SwarmVector(role="Invalid Agent", logic='if print(', target_module="invalid")
    ]
    optimized = nmpc.optimize_mitosis(vectors)
    assert len(optimized) == 1
    assert optimized[0].role == "Valid Agent"

def test_cognitive_nmpc_invalid_import() -> None:
    nmpc = CognitiveNMPC()
    valid_import = 'import json; print(json.dumps({}))'
    score = nmpc.evaluate_template_ast(valid_import)
    assert score == 1.0
    invalid_import = 'import non_existent_library_xyz; print("slop")'
    score = nmpc.evaluate_template_ast(invalid_import)
    assert score < 1.0
