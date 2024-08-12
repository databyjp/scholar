# File: queries.py

from app.utils import COLLECTION_NAME
from weaviate import WeaviateAsyncClient


def hybrid_search(
    client: WeaviateAsyncClient, query_term: str, target_vector: str, limit: int = 10
):
    collection = client.collections.get(COLLECTION_NAME)
    response = collection.query.hybrid(
        query=query_term, target_vector=target_vector, limit=limit
    )
    return response


def rag(
    client: WeaviateAsyncClient,
    prompt: str,
    query_term: str,
    target_vector: str,
    limit: int = 10,
):
    collection = client.collections.get(COLLECTION_NAME)
    response = collection.generate.hybrid(
        query=query_term, target_vector=target_vector, grouped_task=prompt, limit=limit
    )
    return response
