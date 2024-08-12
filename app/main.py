# File: main.py
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from pydantic import BaseModel
from weaviate import WeaviateAsyncClient
from app.utils import COLLECTION_NAME
from typing import List, Optional
from datetime import datetime
import uvicorn

app = FastAPI()

# Initialize Weaviate client
async_client = WeaviateAsyncClient("http://localhost:8080")


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):  # See https://fastapi.tiangolo.com/advanced/events/#lifespan-function
    # Connect the client to Weaviate
    await async_client.connect()
    yield
    # Close the connection to Weaviate
    await async_client.close()


app = FastAPI(lifespan=lifespan)


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


class RAGResult(BaseModel):
    generated_text: str
    search_results: List[SearchResult]


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/search", response_class=HTMLResponse)
async def search(
    request: Request,
    query: str = Form(...),
    target_vector: str = Form(...),
    limit: int = Form(10),
):
    try:
        collection = client.collections.get(COLLECTION_NAME)
        response = await collection.query.hybrid(
            query=query, target_vector=target_vector, limit=limit
        )
        results = [SearchResult(**obj.properties) for obj in response.objects]
        return templates.TemplateResponse(
            "search_results.html", {"request": request, "results": results}
        )
    except Exception as e:
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
        response = await collection.generate.hybrid(
            query=query, target_vector=target_vector, grouped_task=prompt, limit=limit
        )
        result = RAGResult(
            generated_text=response.generated,
            references=[SearchResult(**obj.properties) for obj in response.objects],
        )
        return templates.TemplateResponse(
            "rag_results.html", {"request": request, "result": result}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
