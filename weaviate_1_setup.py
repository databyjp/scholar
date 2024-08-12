import weaviate
import os
from weaviate.classes.config import Property, DataType, Configure, Tokenization
from datetime import datetime

API_KEY_HEADERS = ["ANTHROPIC", "COHERE", "OPENAI"]

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
            name="abstract",
            data_type=DataType.TEXT,
        ),
        Property(
            name="chunk",
            data_type=DataType.TEXT,
        ),
        Property(
            name="authors",
            data_type=DataType.TEXT,
            skip_vectorization=True,
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
            name="abstract",
            source_properties=["abstract"],
        ),
        Configure.NamedVectors.text2vec_cohere(
            name="chunk",
            source_properties=["chunk"],
        ),
        Configure.NamedVectors.text2vec_cohere(
            name="all_text",
            source_properties=["title", "abstract", "chunk"],
        ),
    ],
)

client.close()
