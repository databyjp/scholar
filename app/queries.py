# File: ./app/queries.py

from app.utils import COLLECTION_NAME
from weaviate import WeaviateClient


def hybrid_search(
    client: WeaviateClient, query_term: str, target_vector: str, limit: int = 10
):
    collection = client.collections.get(COLLECTION_NAME)
    response = collection.query.hybrid(
        query=query_term, target_vector=target_vector, limit=limit
    )
    return response


def rag(
    client: WeaviateClient,
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


def get_object_count(
    client: WeaviateClient,
):
    collection = client.collections.get(COLLECTION_NAME)
    response = collection.aggregate.over_all(total_count=True)
    return response.total_count
