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
        query=query_term,
        target_vector=target_vector,
        grouped_task=prompt,
        limit=limit,
        grouped_properties=["chunk"],
    )
    return response


def get_vector_count(
    client: WeaviateClient,
):
    collection = client.collections.get(COLLECTION_NAME)
    response = collection.aggregate.over_all(total_count=True)

    if collection.config.get().vector_config is not None:
        n_vectors = len(collection.config.get().vector_config)
        return response.total_count * n_vectors
    else:
        return response.total_count
