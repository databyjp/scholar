import weaviate
import os
from weaviate.classes.config import Property, DataType, Configure, Tokenization
from pathlib import Path
from extract_text import pdf_to_chunks
import arxiv
import json
from random import randint
from datetime import datetime
from weaviate.util import generate_uuid5

API_KEY_HEADERS = ["ANTHROPIC", "COHERE", "OPENAI"]
DL_DIR = Path("downloaded_papers")

client = weaviate.connect_to_local(
    port=80,
    headers={
        f"X-{API_KEY_HEADER}-API-KEY": os.environ[f"{API_KEY_HEADER}_API_KEY"]
        for API_KEY_HEADER in API_KEY_HEADERS
    },
)

client.collections.delete("Arxiv")

arxiv = client.collections.create(
    name="Arxiv",
    description="A collection of Arxiv papers",
    properties=[
        Property(
            name="title",
            data_type=DataType.TEXT,
        ),
        Property(
            name="summary",
            data_type=DataType.TEXT,
        ),
        Property(
            name="chunk",
            data_type=DataType.TEXT,
        ),
        Property(
            name="authors",
            data_type=DataType.TEXT_ARRAY,
        ),
        Property(
            name="categories",
            data_type=DataType.TEXT_ARRAY,
        ),
        Property(
            name="published",
            data_type=DataType.DATE,
        ),
        Property(
            name="arxiv_id",
            data_type=DataType.TEXT,
            skip_vectorization=True,
            tokenization=Tokenization.FIELD,
        ),
    ],
    vectorizer_config=[
        Configure.NamedVectors.text2vec_cohere(
            name="title",
            source_properties=["title"],
        ),
        Configure.NamedVectors.text2vec_cohere(
            name="summary",
            source_properties=["summary"],
        ),
        Configure.NamedVectors.text2vec_cohere(
            name="chunk",
            source_properties=["chunk"],
        ),
        Configure.NamedVectors.text2vec_cohere(
            name="all_text",
            source_properties=["title", "summary", "chunk"],
        ),
    ],
)


counter = 0
max_docs = 20
total_chunks = 0
chunks_inserted = 0

papers_list = list(DL_DIR.glob("*.pdf"))

print(f"Found {len(papers_list)} papers in the target folder.")

with arxiv.batch.fixed_size(200) as batch:
    for paper in papers_list:

        if counter > max_docs:
            print(f"Max count of {max_docs} reached. Terminating.")
            break

        chunks = pdf_to_chunks(paper)
        metadata = json.loads((DL_DIR / f"{paper.stem}.json").read_text())

        for chunk in chunks:
            properties = {
                "title": metadata["title"],
                "summary": metadata["summary"],
                "chunk": chunk,
                "authors": metadata["authors"],
                "categories": metadata["categories"],
                "arxiv_id": metadata["arxiv_id"],
                "published": datetime.fromisoformat(metadata["published"]),
            }
            batch.add_object(
                properties=properties,
                uuid=generate_uuid5(properties)
            )
            total_chunks += len(chunks)

            if batch.number_errors > 50:
                print(f"Breaking out of insertion loop; as {batch.number_errors} seen out of {total_chunks} object insertions.")
                break

        chunks_inserted += len(chunks)
        counter += 1

if len(arxiv.batch.failed_objects) > 0:
    print(f"Failed to insert {len(arxiv.batch.failed_objects)} objects.")
    for failed_object in arxiv.batch.failed_objects[:5]:
        print(f"Failure: {failed_object.original_uuid}")
        print(failed_object.message)

print(f"Inserted {total_chunks} chunks from {counter} papers.")

client.close()
