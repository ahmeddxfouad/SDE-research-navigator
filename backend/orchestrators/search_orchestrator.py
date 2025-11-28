import os
import requests
from fastapi import FastAPI

app = FastAPI()

PAPER_ADAPTER_URL = os.getenv("PAPER_ADAPTER_URL", "http://research-paper-adapter:80")
UNI_ADAPTER_URL   = os.getenv("UNI_URL", "http://uni-adapter:80")
FILTER_LOGIC_URL  = os.getenv("FILTER_URL", "http://filter-logic:80")

@app.get("/universities")
def get_university_list(q: str = ""):
    """
    Acts as a Bridge. 
    Frontend calls THIS -> This calls Adapter -> Returns list to Frontend.
    """
    try:
        response = requests.get(f"{UNI_ADAPTER_URL}/autocomplete", params={"q": q})
        return response.json()
    except Exception:
        return []

@app.get("/search")
def search_papers(q: str, uni: str = None):
    """
    The Gateway Endpoint.
    1. If 'uni' is empty -> Call Global Search Endpoint.
    2. If 'uni' has text -> Call Institution Search Endpoint.
    """
    
    # University name provided
    if uni and uni.strip():
        print(f"DEBUG: Routing to /search/institution for '{uni}'")
        endpoint = f"{PAPER_ADAPTER_URL}/search/institution"
        params = {"query": q, "uni_name": uni}
        
    # No university name provided
    else:
        print(f"DEBUG: Routing to /search/global")
        endpoint = f"{PAPER_ADAPTER_URL}/search/global"
        params = {"query": q}

    # Execute the call
    try:
        resp = requests.get(endpoint, params=params)
        raw_papers = resp.json().get("papers", [])
        
        print(f"DEBUG: Sending {len(raw_papers)} papers to Filter Logic...")
        
        logic_payload = {"papers": raw_papers}
        logic_resp = requests.post(f"{FILTER_LOGIC_URL}/process", json=logic_payload)
        
        if logic_resp.status_code == 200:
            return logic_resp.json() # Returns sorted, clean data
        else:
            return {"papers": raw_papers}
        
    except Exception as e:
        return {"error": str(e), "papers": []}