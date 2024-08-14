# File: ./preprocessing/3_add_data.py
import weaviate
import os
from pathlib import Path
import json
from datetime import datetime
from weaviate.util import generate_uuid5
import time

EXTRACTED_DIR = Path("extracted_text")
API_KEY_HEADERS = ["ANTHROPIC", "COHERE", "OPENAI"]

# Connect to a local Weaviate instance
client = weaviate.connect_to_local(
    port=8080,
    headers={
        f"X-{API_KEY_HEADER}-API-KEY": os.environ[f"{API_KEY_HEADER}_API_KEY"]
        for API_KEY_HEADER in API_KEY_HEADERS
    },
)

# Get the existing "Arxiv" collection
arxiv = client.collections.get("Arxiv")

chunks_inserted = 0

extracted_files = list(EXTRACTED_DIR.glob("*.json"))

counter = 0
max_docs = len(extracted_files)
# max_docs = 300  # Uncomment this line to limit the number of papers to insert

print(f"Found {len(extracted_files)} extracted files.")

# Start timing
start_time = time.time()

# Use Weaviate's batch insertion for efficient data loading
with arxiv.batch.fixed_size(200) as batch:
    for extracted_file in extracted_files:
        print(f"Processing {extracted_file.stem}...")
        if counter >= max_docs:
            print(f"Max count of {max_docs} reached. Terminating.")
            break

        with open(extracted_file, "r") as f:
            extracted_data = json.load(f)

        metadata = extracted_data["metadata"]
        chunks = extracted_data["chunks"]

        for chunk_no, chunk in enumerate(chunks):
            # Prepare properties for each chunk
            properties = {
                "title": metadata["title"],
                "summary": metadata["summary"],
                "chunk": chunk,
                "chunk_no": chunk_no,
                "authors": metadata["authors"],
                "categories": metadata["categories"],
                "arxiv_id": metadata["arxiv_id"],
                "published": datetime.fromisoformat(metadata["published"]),
            }
            # Add object to the batch with a generated UUID
            batch.add_object(properties=properties, uuid=generate_uuid5(properties))

        # Break if too many errors occur during insertion
        if batch.number_errors > 50:
            print(
                f"Breaking out of insertion loop; as {batch.number_errors} seen out of {chunks_inserted} object insertions."
            )
            break

        chunks_inserted += len(chunks)

        counter += 1

        # Print progress and time taken every 10 papers
        if counter % 10 == 0:
            elapsed_time = time.time() - start_time
            print(
                f"Processed {counter} papers. Time elapsed: {elapsed_time:.2f} seconds"
            )

# End timing
end_time = time.time()
total_time = end_time - start_time

# Check for and report any failed object insertions
if len(arxiv.batch.failed_objects) > 0:
    print(f"Failed to insert {len(arxiv.batch.failed_objects)} objects.")
    for failed_object in arxiv.batch.failed_objects[:5]:
        print(f"Failure: {failed_object.original_uuid}")
        print(failed_object.message)

print(f"Inserted {chunks_inserted} chunks from {counter} papers.")
print(f"Total time taken: {total_time:.2f} seconds")
print(f"Average time per paper: {total_time/counter:.2f} seconds")
print(f"Average time per chunk: {total_time/chunks_inserted:.2f} seconds")

# Close the Weaviate client connection
client.close()
