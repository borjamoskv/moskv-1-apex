#!/usr/bin/env python3
import os
OUTPUT_FILE = "el_espacio_entre_nosotros.md"
ORIGINAL_FILE = "el_espacio_entre_nosotros.md"
def main():
    if os.path.exists(ORIGINAL_FILE):
        with open(ORIGINAL_FILE, "r", encoding="utf-8") as f:
            orig_content = f.read()
    else:
        return
    header_end_idx = orig_content.find("## CAPÍTULO 1:")
    if header_end_idx == -1:
        return
    intro_and_index = orig_content[:header_end_idx]
    ch1_start = orig_content.find("## CAPÍTULO 1:")
    ch1_end = orig_content.find("## CAPÍTULO 2:")
    if ch1_end == -1:
        ch1_end = orig_content.find("# BLOQUE 1:")
    if ch1_start == -1 or ch1_end == -1:
        return
    chapter_1 = orig_content[ch1_start:ch1_end]
    ch30_start = orig_content.find("# CAPÍTULO 30:")
    if ch30_start == -1:
        ch30_start = orig_content.find("## CAPÍTULO 30:")
    if ch30_start == -1:
        return
    chapter_30 = orig_content[ch30_start:]
    ordered_files = [
        "capitulos_raw/bloque_01_cap_02.md",
        "capitulos_raw/bloque_01_caps_03_08.md",
        "expansion_raw/mega_expansion_1_uribarri.md",
        "expansion_raw/bloque_A_caps_085_089.md",
        "capitulos_raw/bloque_02_caps_09_15.md",
        "expansion_raw/mega_expansion_2_usera.md",
        "expansion_raw/bloque_B_caps_151_155.md",
        "expansion_raw/mega_expansion_3_latente.md",
        "capitulos_raw/bloque_03_caps_16_22.md",
        "expansion_raw/bloque_C_caps_221_225.md",
        "capitulos_raw/bloque_04_caps_23_29.md",
        "expansion_raw/mega_expansion_4_final.md",
        "expansion_raw/bloque_D_caps_291_295.md"
    ]
    middle_parts = []
    for filepath in ordered_files:
        if not os.path.exists(filepath):
            continue
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()
            middle_parts.append(content)
    full_text = []
    full_text.append(intro_and_index.strip())
    full_text.append("\n\n---\n\n")
    full_text.append(chapter_1.strip())
    full_text.append("\n\n---\n\n")
    for part in middle_parts:
        full_text.append(part)
        full_text.append("\n\n---\n\n")
    full_text.append(chapter_30.strip())
    consolidated_md = "\n\n".join(full_text)
    new_index = """## ESTRUCTURA DE COMPILACIÓN (ÍNDICE DETALLADO C5-REAL)

1.  **Capítulo 1:** La Fórmula del Silicio y el Caso de Artxanda
2.  **Capítulo 2:** Latencia en la Trinchera de Usera
3.  **Capítulo 3 a 8:** Bloque 1: El Descenso al Latente
4.  **Mega Expansión 1:** Las Crónicas del Silicio del Norte (Siberia Lore)
5.  **Expansión A:** El Asedio al Nodo Vasco (Capítulos 8.5 al 8.9)
6.  **Capítulo 9 a 15:** Bloque 2: Guerra de Nodos en Usera
7.  **Mega Expansión 2:** El Ghetto de Silicio del Sur (Hacker Lore)
8.  **Expansión B:** Diálogos en el Latente (Capítulos 15.1 al 15.5)
9.  **Mega Expansión 3:** La Geometría del Sirimiri Lisérgico (Cortázar Lore)
10. **Capítulo 16 a 22:** Bloque 3: Desdoblamiento Sensorial y Gachas Cuánticas
11. **Expansión C:** La Traición del Hardware (Capítulos 22.1 al 22.5)
12. **Capítulo 23 a 29:** Bloque 4: Preludio al Colapso
13. **Mega Expansión 4:** La Última Resistencia del Cobre (Cobre Lore)
14. **Expansión D:** Los Minutos Negros (Capítulos 29.1 al 29.5)
15. **Capítulo 30:** Amanecer en Usera (Versión Ω)"""
    idx_start = consolidated_md.find("## ESTRUCTURA DE COMPILACIÓN (ÍNDICE)")
    idx_end = consolidated_md.find("---", idx_start) if idx_start != -1 else -1
    if idx_start != -1 and idx_end != -1:
        consolidated_md = consolidated_md[:idx_start] + new_index + "\n\n" + consolidated_md[idx_end:]
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(consolidated_md)
    print("CONSOLIDATED_SUCCESS")
if __name__ == "__main__":
    main()
