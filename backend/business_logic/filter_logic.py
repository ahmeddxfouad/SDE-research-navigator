from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI()

class ProcessRequest(BaseModel):
    papers: List[Dict[str, Any]]

@app.post("/process")
def process_papers(data: ProcessRequest):
    raw_papers = data.papers
    processed_papers = []

    for paper in raw_papers:
        if paper.get("title") and paper.get("year"):
            processed_papers.append(paper)

    processed_papers.sort(key=lambda x: x.get("year") or 0, reverse=True)

    for paper in processed_papers:
        authors = paper.get("authors", [])
        if authors:
            author_name = authors[0].get("name", "Unknown")
            if len(authors) > 1:
                author_display = f"{author_name} et al."
            else:
                author_display = author_name
        else:
            author_display = "Unknown Authors"

        paper["display_citation"] = f"{paper['title']} - {author_display} ({paper['year']})"

    return {"papers": processed_papers, "count": len(processed_papers)}