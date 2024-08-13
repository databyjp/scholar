# File: ./app/main.py
from typing import Literal
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
import anthropic
from openai import OpenAI
from markdown2 import Markdown

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


# Function to generate text using LLM
def generate_text_with_llm(
    context: str, prompt: str, provider: Literal["Anthropic", "OpenAI"] = "Anthropic"
) -> str:
    if provider == "Anthropic":
        llm_response = anthropic.Anthropic().messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": f"Based on the following papers:\n{context}\n\n, respond to the following, and respond in Markdown text: {prompt}",
                }
            ],
        )
        return llm_response.content[0].text

    elif provider == "OpenAI":
        client = OpenAI()

        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": f"Based on the following papers:\n{context}\n\n, respond to the following, and respond in Markdown text: {prompt}",
                },
            ],
        )

        return completion.choices[0].message.content


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
        response = collection.query.hybrid(
            query=query, target_vector=target_vector, limit=limit
        )
        results = [SearchResult(**obj.properties) for obj in response.objects]

        concat_text = "\n=====".join([f"{r.title}\n{r.chunk}" for r in results])

        generated_text = generate_text_with_llm(concat_text, prompt, "Anthropic")

        # Convert markdown to HTML
        markdowner = Markdown()
        generated_html = markdowner.convert(generated_text)

        result = RAGResult(generated_text=generated_html)
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
