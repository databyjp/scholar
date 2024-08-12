import weaviate
import os
# from weaviate.classes.query import
from pathlib import Path

API_KEY_HEADERS = ["ANTHROPIC", "COHERE", "OPENAI"]
DL_DIR = Path("downloaded_papers")

client = weaviate.connect_to_local(
    port=80,
    headers={
        f"X-{API_KEY_HEADER}-API-KEY": os.environ[f"{API_KEY_HEADER}_API_KEY"]
        for API_KEY_HEADER in API_KEY_HEADERS
    },
)

arxiv = client.collections.get("Arxiv")

print(arxiv.aggregate.over_all(total_count=True))


