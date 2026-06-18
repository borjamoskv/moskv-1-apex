import csv
import argparse
from typing import List, Dict

def map_row(row: Dict[str, str]) -> Dict[str, str]:
    mapped = {}
    mapped['user_email_address'] = row.get('user_email_address') or row.get('Email') or row.get('email') or ''
    mapped['user_name'] = row.get('user_name') or row.get('Name') or row.get('name') or ''
    mapped['num_unique_web_posts_seen'] = row.get('num_unique_web_posts_seen') or row.get('Unique posts seen') or '0'
    mapped['days_active_last_30d'] = row.get('days_active_last_30d') or row.get('Days active (30d)') or '0'
    mapped['num_web_post_views'] = row.get('num_web_post_views') or row.get('Post views') or '0'
    mapped['num_emails_received'] = row.get('num_emails_received') or row.get('Emails received (6mo)') or '0'
    return mapped

def compute_exergy(row: Dict[str, str], alpha: float = 2.0, beta: float = 1.5, gamma: float = 1.0) -> float:
    """
    X_i = alpha * U_i + beta * D_i + gamma * V_i
    Donde:
      U_i = Unique posts seen (num_unique_web_posts_seen)
      D_i = Days active (days_active_last_30d)
      V_i = Views (num_web_post_views)
    """
    def safe_float(val: str) -> float:
        try:
            return float(val) if val else 0.0
        except ValueError:
            return 0.0

    mapped = map_row(row)
    U = safe_float(mapped.get('num_unique_web_posts_seen', 0))
    D = safe_float(mapped.get('days_active_last_30d', 0))
    V = safe_float(mapped.get('num_web_post_views', 0))

    return (alpha * U) + (beta * D) + (gamma * V)

import json
import os

def export_thermal_mass(subscribers: List[Dict], export_path: str = "thermal_mass.json", e_threshold: int = 10, exergy_threshold: float = 1.0):
    # Masa Térmica: Alta energía enviada (E), baja conversión a trabajo (Exergía)
    thermal_mass = [s for s in subscribers if float(s['E']) >= e_threshold and float(s['exergy']) < exergy_threshold]
    
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), export_path)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({"metadata": {"description": "Substack Thermal Mass extracted for OSINT resolution"}, "leads": thermal_mass}, f, indent=2)
    print(f"\n[+] MASA TÉRMICA AISLADA: {len(thermal_mass)} nodos exportados a {out_path}.")

def analyze_substack_exergy(csv_path: str, top_n: int = 20, export_thermal: bool = False):
    print(f"[C5-REAL] Parseando mapa termodinámico desde: {csv_path}")
    subscribers = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            mapped = map_row(row)
            if not mapped.get('user_email_address'):
                continue
            
            def safe_float(val: str) -> float:
                try: return float(val) if val else 0.0
                except ValueError: return 0.0

            exergy_score = compute_exergy(mapped)
            subscribers.append({
                'email': mapped['user_email_address'],
                'name': mapped.get('user_name', ''),
                'exergy': exergy_score,
                'U': safe_float(mapped.get('num_unique_web_posts_seen', 0)),
                'D': safe_float(mapped.get('days_active_last_30d', 0)),
                'V': safe_float(mapped.get('num_web_post_views', 0)),
                'E': safe_float(mapped.get('num_emails_received', 0))
            })

    # Sort by descending exergy
    subscribers.sort(key=lambda x: x['exergy'], reverse=True)

    print("\n[+] NODOS DE MÁXIMA EXERGÍA (Top Core-Readers):\n")
    print(f"{'EMAIL':<35} | {'EXERGY (X)':<10} | {'UNIQUE (U)':<10} | {'DAYS (D)':<10} | {'VIEWS (V)':<10} | {'EMAILS (E)':<10}")
    print("-" * 100)
    for s in subscribers[:top_n]:
        print(f"{s['email']:<35} | {s['exergy']:<10.2f} | {s['U']:<10} | {s['D']:<10} | {s['V']:<10} | {s['E']:<10}")
        
    if export_thermal:
        export_thermal_mass(subscribers)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Substack Exergy Calculator")
    parser.add_argument("csv_path", help="Path to Substack subscribers.csv")
    parser.add_argument("--export-thermal-mass", action="store_true", help="Export thermal mass (low exergy, high emails) to JSON")
    args = parser.parse_args()
    
    analyze_substack_exergy(args.csv_path, export_thermal=args.export_thermal_mass)
