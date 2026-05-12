import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import Optional
import uuid

from config import settings
from knowledge.embeddings import embed_texts, embed_query

_client: chromadb.PersistentClient | None = None
COLLECTION_NAME = "oms_knowledge"


def get_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
    return _client


def get_collection():
    client = get_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def add_documents(
    texts: list[str],
    metadatas: list[dict],
    ids: Optional[list[str]] = None,
) -> list[str]:
    collection = get_collection()
    doc_ids = ids or [str(uuid.uuid4()) for _ in texts]
    embeddings = embed_texts(texts)
    collection.add(
        ids=doc_ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )
    return doc_ids


def search(
    query: str,
    n_results: int = 5,
    where: Optional[dict] = None,
) -> list[dict]:
    collection = get_collection()
    query_embedding = embed_query(query)

    kwargs: dict = {
        "query_embeddings": [query_embedding],
        "n_results": min(n_results, collection.count() or 1),
        "include": ["documents", "metadatas", "distances"],
    }
    if where:
        kwargs["where"] = where

    results = collection.query(**kwargs)

    output = []
    if not results["ids"] or not results["ids"][0]:
        return output

    for i, doc_id in enumerate(results["ids"][0]):
        output.append({
            "id": doc_id,
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "score": 1 - results["distances"][0][i],  # cosine similarity
        })
    return output


def delete_document(doc_id: str) -> None:
    get_collection().delete(ids=[doc_id])


def count_documents() -> int:
    return get_collection().count()
