import os
import requests
from fastapi import FastAPI

app = FastAPI()

PAPER_ADAPTER_URL = os.getenv("PAPER_ADAPTER_URL", "http://research-paper-adapter:80")
# ... other URLs ...

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
        
        # (Optional) Send to Logic Layer for sorting...
        return {"papers": raw_papers}
        
    except Exception as e:
        return {"error": str(e), "papers": []}