import weaviate
import os
from pathlib import Path
from preprocessing.helpers import pdf_to_chunks
import arxiv
import json
from random import randint
from datetime import datetime
from weaviate.util import generate_uuid5
from pathlib import Path


DL_DIR = Path("downloaded_papers")
API_KEY_HEADERS = ["ANTHROPIC", "COHERE", "OPENAI"]

# Connect to a local Weaviate instance
client = weaviate.connect_to_local(
    port=80,
    headers={
        f"X-{API_KEY_HEADER}-API-KEY": os.environ[f"{API_KEY_HEADER}_API_KEY"]
        for API_KEY_HEADER in API_KEY_HEADERS
    },
)

# Get the existing "Arxiv" collection
arxiv = client.collections.get("Arxiv")

total_chunks = 0
chunks_inserted = 0

papers_list = list(DL_DIR.glob("*.pdf"))

counter = 0
max_docs = len(papers_list)
# max_docs = 10  # Uncomment this line to limit the number of papers to insert

print(f"Found {len(papers_list)} papers in the target folder.")

# Use Weaviate's batch insertion for efficient data loading
with arxiv.batch.fixed_size(200) as batch:
    for paper in papers_list:
        if counter > max_docs:
            print(f"Max count of {max_docs} reached. Terminating.")
            break

        chunks = pdf_to_chunks(paper)
        metadata = json.loads((DL_DIR / f"{paper.stem}.json").read_text())

        for chunk in chunks:
            # Prepare properties for each chunk
            properties = {
                "title": metadata["title"],
                "summary": metadata["summary"],
                "chunk": chunk,
                "authors": metadata["authors"],
                "categories": metadata["categories"],
                "arxiv_id": metadata["arxiv_id"],
                "published": datetime.fromisoformat(metadata["published"]),
            }
            # Add object to the batch with a generated UUID
            batch.add_object(properties=properties, uuid=generate_uuid5(properties))
            total_chunks += len(chunks)

            # Break if too many errors occur during insertion
            if batch.number_errors > 50:
                print(
                    f"Breaking out of insertion loop; as {batch.number_errors} seen out of {total_chunks} object insertions."
                )
                break

        chunks_inserted += len(chunks)
        counter += 1

# Check for and report any failed object insertions
if len(arxiv.batch.failed_objects) > 0:
    print(f"Failed to insert {len(arxiv.batch.failed_objects)} objects.")
    for failed_object in arxiv.batch.failed_objects[:5]:
        print(f"Failure: {failed_object.original_uuid}")
        print(failed_object.message)

print(f"Inserted {total_chunks} chunks from {counter} papers.")

# Close the Weaviate client connection
client.close()
