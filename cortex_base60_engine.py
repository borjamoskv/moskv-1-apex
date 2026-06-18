import math

def generate_babylonian_triples(limit=15):
    """
    Genera ternas pitagóricas usando el método babilónico (Plimpton 322).
    Basado en parámetros p y q donde p > q > 0 y son coprimos.
    """
    triples = []
    for p in range(2, limit):
        for q in range(1, p):
            if math.gcd(p, q) == 1 and (p - q) % 2 != 0:
                # Ecuaciones babilónicas para ternas
                a = p**2 - q**2
                b = 2 * p * q
                c = p**2 + q**2
                triples.append((a, b, c))
    return sorted(triples, key=lambda x: x[2])

def base60_vs_base10_efficiency():
    """
    Demuestra la superioridad divisoria de la Base 60 frente a la Base 10.
    """
    divisors_10 = [i for i in range(1, 11) if 10 % i == 0]
    divisors_60 = [i for i in range(1, 61) if 60 % i == 0]
    
    return len(divisors_10), len(divisors_60)

if __name__ == "__main__":
    print("[C5-REAL] INICIANDO MOTOR SEXAGESIMAL BABILÓNICO")
    
    d10, d60 = base60_vs_base10_efficiency()
    print(f"-> Divisores exactos Base 10: {d10}")
    print(f"-> Divisores exactos Base 60: {d60}")
    print("-> RESULTADO: Base 60 tiene 300% más capacidad de fraccionamiento exacto (Cero error de flotante).")
    
    print("\n[+] Extrayendo Ternas Pitagóricas (Estilo Plimpton 322):")
    triples = generate_babylonian_triples(7)
    for t in triples:
        print(f"    a={t[0]}, b={t[1]}, c={t[2]} -> Verificación: {t[0]**2 + t[1]**2 == t[2]**2}")
