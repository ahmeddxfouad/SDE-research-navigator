import requests
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Research Paper Adapter", version="4.0")

SEMANTIC_API_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

def _call_external_api(final_query_string: str, limit: int):
    print(f"DEBUG: Calling Semantic Scholar with: '{final_query_string}'")
    
    params = {
        "query": final_query_string,
        "limit": limit,
        "fields": "paperId,title,abstract,year,authors,venue,url" 
    }

    try:
        response = requests.get(SEMANTIC_API_URL, params=params, timeout=10)
        
        if response.status_code != 200:
            return {"papers": [], "total": 0}

        data = response.json()
        return {"papers": data.get("data", []), "total": data.get("total", 0)}

    except Exception as e:
        print(f"ERROR: {e}")
        raise HTTPException(status_code=500, detail="External API Error")

@app.get("/search/global")
def search_global(query: str, limit: int = 20):
    """
    Searches ONLY by topic.
    Example: "Machine Learning"
    """
    return _call_external_api(query, limit)

# --- ENDPOINT 2: Institutional Search ---
@app.get("/search/institution")
def search_by_institution(query: str, uni_name: str, limit: int = 20):
    """
    Searches by Topic + University Name.
    Example: "Machine Learning" + "Harvard" -> "Machine Learning 'Harvard'"
    """
    # Construct the specific query string here
    # Adding quotes around uni_name forces a stricter match
    combined_query = f'{query} "{uni_name}"'
    
    return _call_external_api(combined_query, limit)