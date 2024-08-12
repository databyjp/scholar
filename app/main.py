# File: main.py
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pydantic import BaseModel
from weaviate import WeaviateClient
from app.utils import COLLECTION_NAME, get_weaviate_client
from typing import List, Optional
from datetime import datetime
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Weaviate client
client = get_weaviate_client()


app = FastAPI()


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
        collection = client.collections.get(COLLECTION_NAME)
        response = collection.generate.hybrid(
            query=query, target_vector=target_vector, grouped_task=prompt, limit=limit
        )
        result = RAGResult(
            generated_text=response.generated,
            references=[SearchResult(**obj.properties) for obj in response.objects],
        )
        return templates.TemplateResponse(
            request=request, name="rag_results.html", context={"result": result}
        )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
