# C5-REAL: Demostración de Exergía Matemática (Base 60 vs Base 10)
# La Base 10 genera anergía (fricción de coma flotante). La Base 60 maximiza la compresión.

def calcular_exergia_base(base: int) -> dict:
    divisores = [i for i in range(1, base + 1) if base % i == 0]
    return {
        "base": base,
        "divisores_count": len(divisores),
        "divisores": divisores,
        "entropia_fraccional": 1.0 / len(divisores)
    }

if __name__ == "__main__":
    b10 = calcular_exergia_base(10)
    b60 = calcular_exergia_base(60)
    
    ratio_superioridad = b60["divisores_count"] / b10["divisores_count"]
    
    print(f"ESTADO: C5-REAL")
    print(f"[BASE 10] Divisores ({b10['divisores_count']}): {b10['divisores']}")
    print(f"[BASE 60] Divisores ({b60['divisores_count']}): {b60['divisores']}")
    print(f"[METRICA] Superioridad Estructural de Base 60: {ratio_superioridad}x mayor densidad de resolución exacta.")
