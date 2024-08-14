# File: ./app/utils.py

import weaviate
from weaviate import WeaviateClient
from pathlib import Path
import os


DL_DIR = Path("downloaded_papers")
COLLECTION_NAME = "Arxiv"


def get_weaviate_client() -> WeaviateClient:
    API_KEY_HEADERS = ["ANTHROPIC", "COHERE", "OPENAI"]

    # Connect to a local Weaviate instance
    client = weaviate.connect_to_local(
        port=8080,
        headers={
            f"X-{API_KEY_HEADER}-API-KEY": os.environ[f"{API_KEY_HEADER}_API_KEY"]
            for API_KEY_HEADER in API_KEY_HEADERS
        },
    )
    return client
