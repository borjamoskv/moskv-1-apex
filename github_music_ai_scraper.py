import os
import time
import requests
import json

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}" if GITHUB_TOKEN else "",
    "Accept": "application/vnd.github.v3+json"
}

def search_repos(query):
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/search/repositories?q={query}&per_page=100&page={page}"
        print(f"[*] Fetching page {page} for query: {query}")
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 403:
            print("[!] Rate limit hit. Sleeping for 60 seconds...")
            time.sleep(60)
            continue
            
        if response.status_code != 200:
            print(f"[!] Error {response.status_code}: {response.text}")
            break
            
        data = response.json()
        items = data.get("items", [])
        if not items:
            break
            
        repos.extend(items)
        if len(items) < 100:
            break
        page += 1
        time.sleep(2)
        
    return repos

def get_user_details(username):
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    return None

def main():
    queries = [
        '"electronic music" "AI"',
        '"electronic music" "machine learning"',
        '"techno" "machine learning"',
        '"synthesizer" "AI"'
    ]
    
    unique_owners = set()
    
    for q in queries:
        print(f"[*] Executing search: {q}")
        found = search_repos(q)
        for repo in found:
            owner = repo.get("owner", {}).get("login")
            if owner and repo.get("owner", {}).get("type") == "User":
                unique_owners.add(owner)
                
    print(f"[*] Found {len(unique_owners)} unique profile owners. Extracting emails...")
    
    results = []
    
    for idx, username in enumerate(unique_owners):
        details = get_user_details(username)
        if not details:
            continue
            
        email = details.get("email")
        if email:
            results.append({
                "username": username,
                "name": details.get("name", ""),
                "email": email,
                "bio": details.get("bio", ""),
                "company": details.get("company", ""),
                "location": details.get("location", ""),
                "url": details.get("html_url", "")
            })
            print(f"[+] Found email for {username}: {email}")
            
        if (idx + 1) % 10 == 0:
            time.sleep(1)
            
    with open("music_ai_leads.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
        
    print(f"[*] Done. Saved {len(results)} verifiable leads to music_ai_leads.json")

if __name__ == "__main__":
    main()
