# File: ./app/main.py
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from app.utils import COLLECTION_NAME, get_weaviate_client
from app.queries import get_object_count
from typing import List, Optional
from datetime import datetime
import uvicorn
import subprocess
import re

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Weaviate client
client = get_weaviate_client()

class SearchRequest(BaseModel):
    query: str
    target_vector: str
    limit: Optional[int] = 10

class SearchResult(BaseModel):
    title: str
    summary: str
    chunk: str
    chunk_no: int
    authors: List[str]
    categories: List[str]
    published: datetime
    arxiv_id: str

class RAGResult(BaseModel):
    generated_text: str
    references: List[SearchResult]

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/search", response_class=HTMLResponse)
async def search(
    request: Request,
    query: str = Form(...),
    target_vector: str = Form(...),
    limit: int = Form(10),
):
    try:
        collection = client.collections.get(COLLECTION_NAME)
        response = collection.query.hybrid(
            query=query, target_vector=target_vector, limit=limit
        )
        results = [SearchResult(**obj.properties) for obj in response.objects]
        return templates.TemplateResponse(
            request=request, name="search_results.html", context={"results": results}
        )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rag", response_class=HTMLResponse)
async def rag(
    request: Request,
    prompt: str = Form(...),
    query: str = Form(...),
    target_vector: str = Form(...),
    limit: int = Form(10),
):
    try:
        # Placeholder implementation
        generated_text = f"This is a placeholder generated text for the prompt: {prompt}"
        references = [
            SearchResult(
                title="Placeholder Title",
                summary="Placeholder summary",
                chunk="Placeholder chunk",
                chunk_no=1,
                authors=["Author 1", "Author 2"],
                categories=["Category 1", "Category 2"],
                published=datetime.now(),
                arxiv_id="0000.00000"
            )
        ]
        result = RAGResult(generated_text=generated_text, references=references)
        return templates.TemplateResponse(
            request=request, name="rag_results.html", context={"result": result}
        )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memory_usage")
async def memory_usage():
    try:
        # Run the go tool pprof command and capture its output
        result = subprocess.run(
            ["go", "tool", "pprof", "-top", "http://localhost:6060/debug/pprof/heap"],
            capture_output=True,
            text=True,
            timeout=10,  # Set a timeout to prevent hanging
        )

        if result.returncode == 0:
            # Parse the output to get the total memory usage
            match = re.search(
                r"Showing nodes accounting for (\d+\.?\d*)MB, (\d+\.?\d*)% of (\d+\.?\d*)MB total",
                result.stdout,
            )
            if match:
                total_mb = float(match.group(3))
                return JSONResponse({"total_mb": total_mb})
        else:
            print(f"Error running pprof: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("Timeout error running pprof")
    except Exception as e:
        print(f"Error fetching memory usage: {e}")

    raise HTTPException(status_code=500, detail="Failed to fetch memory usage")


@app.get("/object_count")
async def object_count():
    try:
        count = get_object_count(client)
        return JSONResponse({"count": count})
    except Exception as e:
        print(f"Error fetching object count: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch object count")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
