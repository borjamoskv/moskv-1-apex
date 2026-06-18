def transistor_switch(voltage_in, threshold=0.5):
    """
    Simula el comportamiento de un transistor de silicio dopado (semiconductor).
    Si el voltaje supera el umbral, la compuerta se abre (conduce = 1).
    Si no, permanece como aislante (no conduce = 0).
    """
    return 1 if voltage_in >= threshold else 0

def nand_gate(a_voltage, b_voltage):
    """
    Simula una compuerta NAND, el bloque de construcción fundamental de la computación,
    usando transistores de silicio.
    """
    a_state = transistor_switch(a_voltage)
    b_state = transistor_switch(b_voltage)
    return 0 if (a_state == 1 and b_state == 1) else 1

if __name__ == "__main__":
    print("[C5-REAL] INICIANDO SIMULACIÓN DE COMPUERTA LÓGICA DE SILICIO (NAND)")
    
    test_cases = [(0.0, 0.0), (0.0, 1.0), (1.0, 0.0), (1.0, 1.0)]
    
    for v1, v2 in test_cases:
        output = nand_gate(v1, v2)
        print(f"Voltaje In: ({v1}v, {v2}v) -> Estado Transistores: ({int(v1)}, {int(v2)}) -> Output Lógico: {output}")
        
    print("-> RESULTADO: La lógica booleana ha sido ejecutada alterando el estado de conducción del silicio.")
