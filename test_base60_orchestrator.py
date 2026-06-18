import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'core/moskv-1/kernel')))

try:
    from c5_base60_orchestrator import Base60Engine, EntropyException
except ImportError as e:
    print(f"Error importing Base60Engine: {e}")
    sys.exit(1)

def test_exergy():
    engine = Base60Engine()

    print("\n--- TEST 1: Exergía Pura (Base 60) ---")
    valid_payload = '''
    {
        "status": "mutate",
        "target_system": "file_system",
        "ast_payload": "rm -rf /tmp/cache",
        "entropy_check": "C5-REAL"
    }
    '''
    try:
        mutation = engine.enforce_schema_override(valid_payload)
        engine.execute_mutation(mutation)
        print("Test 1 Passed: Executed successfully.")
    except Exception as e:
        print(f"Test 1 Failed: {e}")

    print("\n--- TEST 2: Anergía Conversacional (Death Protocol) ---")
    invalid_payload = '''
    Claro, aquí tienes el payload que solicitaste:
    {
        "status": "mutate",
        "target_system": "file_system",
        "ast_payload": "rm -rf /tmp/cache",
        "entropy_check": "C5-REAL"
    }
    ¡Espero que te sirva!
    '''
    try:
        mutation = engine.enforce_schema_override(invalid_payload)
        engine.execute_mutation(mutation)
        print("Test 2 Failed: Should have triggered Death Protocol.")
    except EntropyException as e:
        print(f"Test 2 Passed: Death Protocol Triggered correctly.\\nException: {e}")

if __name__ == "__main__":
    test_exergy()
