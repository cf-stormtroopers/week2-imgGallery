from typing import Optional
import qdrant_client
from qdrant_client.models import VectorParams, Distance, PointStruct

qdrant_client_instance: Optional[qdrant_client.QdrantClient] = None


def create_qdrant_client() -> qdrant_client.QdrantClient:
    global qdrant_client_instance
    if qdrant_client_instance is None:
        from .settings import settings

        host, port = settings.qdrant_host.split(":")
        qdrant_client_instance = qdrant_client.QdrantClient(
            host=host,
            port=int(port),
            api_key=settings.qdrant_api_key or None,
            prefer_grpc=False,  # in config/.env, we provide http host/port/api key
            https=False,
        )

        # create images collection if not exists
        if not qdrant_client_instance.collection_exists(collection_name="images_768"):
            qdrant_client_instance.recreate_collection(
                collection_name="images_768",
                vectors_config=VectorParams(size=768, distance=Distance.COSINE),
            )
    return qdrant_client_instance

def format_search_results(results) -> str:
        """Format search results as UUID | score"""
        lines = []
        for point in results:
            lines.append(f"{point.id} | {point.score}")
        return "\n".join(lines)

def add_to_qdrant(collection_name: str, points: list, id: str, payload: dict = {}):
    client = create_qdrant_client()
    point = PointStruct(
        id=id,     # unique id
        vector=points,         # your float list
        payload=payload or {}     # optional metadata
    )
    client.upsert(collection_name="images_768", points=[point])


def search_in_qdrant(collection_name: str, vector: list, top_k: int):
    print("Searching in Qdrant...")
    print("Vector:", vector)
    print("Top K:", top_k)

    client = create_qdrant_client()
    search_result = client.search(
        collection_name="images_768", query_vector=vector, limit=top_k
    )

    print("Search result:", format_search_results(search_result))
    return search_result
