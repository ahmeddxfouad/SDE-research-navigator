import requests
from fastapi import FastAPI

app = FastAPI(title="University Domain Adapter", version="2.1")

UNI_LIST_URL = "https://raw.githubusercontent.com/Hipo/university-domains-list/master/world_universities_and_domains.json"
UNIVERSITY_DATA_CACHE = []

def load_data():
    global UNIVERSITY_DATA_CACHE
    try:
        response = requests.get(UNI_LIST_URL, timeout=10)
        if response.status_code == 200:
            UNIVERSITY_DATA_CACHE = response.json()
            print(f"DEBUG: Loaded {len(UNIVERSITY_DATA_CACHE)} universities.")
    except Exception as e:
        print(f"ERROR: {e}")

@app.on_event("startup")
async def startup_event():
    load_data()

@app.get("/autocomplete")
def autocomplete_universities(q: str = ""):
    """
    If 'q' is empty: Returns the first 10 universities (Default view).
    If 'q' has text: Returns search results.
    """
    if not UNIVERSITY_DATA_CACHE:
        load_data()

    results = []
    
    # Empty search
    if not q:
        count = 0
        for uni in UNIVERSITY_DATA_CACHE:
            if uni.get('domains'):
                results.append({
                    "name": uni['name'],
                    "domain": uni['domains'][0]
                })
                count += 1
            if count >= 10:
                break
        return results

    # Search with query
    query = q.lower()
    count = 0
    for uni in UNIVERSITY_DATA_CACHE:
        if query in uni['name'].lower():
            if uni.get('domains'):
                results.append({
                    "name": uni['name'],
                    "domain": uni['domains'][0]
                })
                count += 1
        if count >= 10: 
            break
            
    return results