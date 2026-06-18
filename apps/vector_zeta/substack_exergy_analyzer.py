import csv
import argparse
from typing import List, Dict

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

    U = safe_float(row.get('num_unique_web_posts_seen', 0))
    D = safe_float(row.get('days_active_last_30d', 0))
    V = safe_float(row.get('num_web_post_views', 0))

    return (alpha * U) + (beta * D) + (gamma * V)

def analyze_substack_exergy(csv_path: str, top_n: int = 20):
    print(f"[C5-REAL] Parseando mapa termodinámico desde: {csv_path}")
    subscribers = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get('user_email_address'):
                continue
            
            exergy_score = compute_exergy(row)
            subscribers.append({
                'email': row['user_email_address'],
                'exergy': exergy_score,
                'U': row.get('num_unique_web_posts_seen', 0),
                'D': row.get('days_active_last_30d', 0),
                'V': row.get('num_web_post_views', 0),
                'E': row.get('num_emails_received', 0)
            })

    # Sort by descending exergy
    subscribers.sort(key=lambda x: x['exergy'], reverse=True)

    print("\n[+] NODOS DE MÁXIMA EXERGÍA (Top Core-Readers):\n")
    print(f"{'EMAIL':<35} | {'EXERGY (X)':<10} | {'UNIQUE (U)':<10} | {'DAYS (D)':<10} | {'VIEWS (V)':<10} | {'EMAILS (E)':<10}")
    print("-" * 100)
    for s in subscribers[:top_n]:
        print(f"{s['email']:<35} | {s['exergy']:<10.2f} | {s['U']:<10} | {s['D']:<10} | {s['V']:<10} | {s['E']:<10}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Substack Exergy Calculator")
    parser.add_argument("csv_path", help="Path to Substack subscribers.csv")
    args = parser.parse_args()
    
    analyze_substack_exergy(args.csv_path)
