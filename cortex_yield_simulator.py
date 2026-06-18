import random

def simulate_wafer_yield(defect_rate, total_chips=1000):
    """
    Simula el rendimiento (yield) de una oblea de silicio de última generación.
    Un chip falla si es impactado por un defecto (polvo, error cuántico).
    """
    working_chips = 0
    for _ in range(total_chips):
        if random.random() > defect_rate:
            working_chips += 1
    return working_chips

if __name__ == "__main__":
    print("[C5-REAL] INICIANDO SIMULADOR DE RENDIMIENTO LITOGRÁFICO (YIELD)")
    
    # TSMC (Taiwan) - Cultura obsesiva, clúster cerrado, baja tasa de defectos
    tsmc_defect_rate = 0.08
    # Competencia (Intel/Samsung) - Alta tecnología, pero sin el ecosistema perfecto de Hsinchu
    competitor_defect_rate = 0.45
    
    cost_per_wafer = 20000  # Dólares
    
    tsmc_yield = simulate_wafer_yield(tsmc_defect_rate)
    comp_yield = simulate_wafer_yield(competitor_defect_rate)
    
    print(f"-> TSMC Yield: {tsmc_yield}/1000 chips funcionales ({(tsmc_yield/1000)*100}%)")
    print(f"   Costo real por chip funcional: ${round(cost_per_wafer/tsmc_yield, 2)}")
    
    print(f"-> Competencia Yield: {comp_yield}/1000 chips funcionales ({(comp_yield/1000)*100}%)")
    print(f"   Costo real por chip funcional: ${round(cost_per_wafer/comp_yield, 2)}")
    
    print("\n[!] CONCLUSIÓN ESTRUCTURAL:")
    print("La tecnología EUV es idéntica, pero la cultura de ejecución hace que el chip de TSMC sea económicamente viable y el de la competencia genere pérdidas masivas.")
