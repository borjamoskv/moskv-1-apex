import os
import time
import requests
import pandas as pd

# C5-REAL: Motor extractivo de exergía - GitHub Leads
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Accept": "application/vnd.github.v3+json"
}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"

QUERIES = ["JUCE", "VST3", "Librosa", "Audio-AI"]
RATE_LIMIT_DELAY = 2.0

def search_users(query):
    """Extrae dueños de repositorios que coinciden con el query."""
    print(f"[+] Ingesta estructural: {query}")
    users = []
    url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc"
    
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 401 and "Authorization" in HEADERS:
        print("[-] Token invu00e1lido (401). Reintentando sin token...")
        del HEADERS["Authorization"]
        response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        items = response.json().get("items", [])
        for item in items:
            owner = item.get("owner", {})
            if owner.get("type") == "User":
                users.append(owner.get("login"))
    else:
        print(f"[-] Falla bizantina en query {query}: {response.text}")
        
    return list(set(users))

def get_user_email(username):
    """Fuerza la resolución del email si es público."""
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 401 and "Authorization" in HEADERS:
        print("[-] Token invu00e1lido (401). Reintentando sin token...")
        del HEADERS["Authorization"]
        response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        return {
            "username": username,
            "name": data.get("name"),
            "email": data.get("email"),
            "bio": data.get("bio")
        }
    return None

def main():
    if not GITHUB_TOKEN:
        print("[!] Advertencia: GITHUB_TOKEN nulo. Ejecución sometida a rate limit asimétrico.")
        
    all_users = set()
    for q in QUERIES:
        all_users.update(search_users(q))
        time.sleep(RATE_LIMIT_DELAY)
        
    print(f"[+] Entidad Swarm identificada: {len(all_users)} nodos.")
    
    leads = []
    # Límite por defecto a 100 para evitar bloqueos térmicos de API sin auth
    for username in list(all_users)[:100]: 
        data = get_user_email(username)
        if data and data["email"]:
            leads.append(data)
            print(f"[+] Exergía confirmada: {data['email']} ({username})")
        time.sleep(0.5)
        
    if leads:
        df = pd.DataFrame(leads)
        output_file = "audio_ai_leads.csv"
        df.to_csv(output_file, index=False)
        print(f"[+] Grafo cristalizado en disco: {len(leads)} firmas en {output_file}")
    else:
        print("[-] Cero anergía: No se resolvieron correos públicos en esta cohorte.")

if __name__ == "__main__":
    main()
