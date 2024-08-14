# File: ./preprocessing/2_create_collection.py
from weaviate.classes.config import Property, DataType, Configure, Tokenization
import weaviate
from pathlib import Path
import os


DL_DIR = Path("downloaded_papers")
API_KEY_HEADERS = ["ANTHROPIC", "COHERE", "OPENAI"]

# Connect to a local Weaviate instance
client = weaviate.connect_to_local(
    port=8080,
    headers={
        f"X-{API_KEY_HEADER}-API-KEY": os.environ[f"{API_KEY_HEADER}_API_KEY"]
        for API_KEY_HEADER in API_KEY_HEADERS
    },
)

# Delete existing "Arxiv" collection if it exists
client.collections.delete("Arxiv")

# Create a new "Arxiv" collection with specified properties and vectorizer configuration
arxiv = client.collections.create(
    name="Arxiv",
    description="A collection of Arxiv papers",
    properties=[
        # Define properties for the Arxiv collection
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
            name="chunk_no",
            data_type=DataType.INT,
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
            skip_vectorization=True,  # Don't vectorize this field
            tokenization=Tokenization.FIELD,  # Treat the entire field as a single token
        ),
    ],
    vectorizer_config=[
        # Configure named vectors for different property combinations
        Configure.NamedVectors.text2vec_cohere(
            name="chunk",
            source_properties=["chunk"],
            vector_index_config=Configure.VectorIndex.hnsw(),
        ),
        Configure.NamedVectors.text2vec_cohere(
            name="all_text",
            source_properties=["title", "summary", "chunk"],
            vector_index_config=Configure.VectorIndex.hnsw(),
        ),
    ],
    generative_config=Configure.Generative.cohere(model="command-r-plus"),
)

client.close()
