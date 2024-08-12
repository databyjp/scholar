# File: utils.py

import weaviate
from weaviate import WeaviateAsyncClient
from pathlib import Path
import os


DL_DIR = Path("downloaded_papers")
COLLECTION_NAME = "Arxiv"


def get_weaviate_client() -> WeaviateAsyncClient:
    API_KEY_HEADERS = ["ANTHROPIC", "COHERE", "OPENAI"]

    # Connect to a local Weaviate instance
    client = weaviate.use_async_with_local(
        port=80,
        headers={
            f"X-{API_KEY_HEADER}-API-KEY": os.environ[f"{API_KEY_HEADER}_API_KEY"]
            for API_KEY_HEADER in API_KEY_HEADERS
        },
    )
    return client
