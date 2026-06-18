import os
import re

def calculate_exergy_score(directory_path="."):
    """
    Escanea el directorio en busca de "Anergía" (ruido corporativo, LLM slop, fricción sintáctica).
    Calcula un score de Exergía (Densidad de Señal).
    """
    slop_patterns = [
        r"(?i)espero que esto ayude",
        r"(?i)aquí tienes el código",
        r"(?i)//\s*TODO:",
        r"(?i)print\(''\)", # Prints vacíos
        r"(?i)pass\n"       # Funciones vacías
    ]
    
    total_lines = 0
    anergy_lines = 0
    scanned_files = 0
    
    for root, _, files in os.walk(directory_path):
        if ".git" in root or "__pycache__" in root:
            continue
            
        for file in files:
            if file.endswith((".py", ".md", ".txt")):
                file_path = os.path.join(root, file)
                scanned_files += 1
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        for line in f:
                            total_lines += 1
                            if any(re.search(pattern, line) for pattern in slop_patterns):
                                anergy_lines += 1
                except Exception:
                    pass
                    
    if total_lines == 0:
        return 1.0
        
    exergy_score = 1.0 - (anergy_lines / total_lines)
    return exergy_score, anergy_lines, total_lines, scanned_files

if __name__ == "__main__":
    print("[C5-REAL] INICIANDO AUDITORÍA DE ANERGÍA ESTRUCTURAL (MOSKV-1 LINTER)")
    
    score, anergy, total, files = calculate_exergy_score()
    
    print(f"-> Archivos escaneados: {files}")
    print(f"-> Líneas de código totales: {total}")
    print(f"-> Líneas de Anergía (Fricción/Slop): {anergy}")
    print(f"-> SCORE DE EXERGÍA: {score * 100:.2f}%")
    
    if score < 0.95:
        print("\n[!] ALERTA DE SISTEMA: El nivel de Exergía ha caído por debajo del umbral del Operador Soberano (95%). Purga requerida.")
    else:
        print("\n[+] SISTEMA ESTABLE. Densidad de señal óptima validada.")
