from typing import List, Dict
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from app.core.config import settings

client = QdrantClient(path=settings.VECTOR_DB_PATH)
client.set_model("sentence-transformers/all-MiniLM-L6-v2")


def add_document(
    text: str,
    file_id: int,
    user_id: int,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    collection_name: str = "documents",
) -> int:
    """Chunk text and add to vector store. Returns number of chunks added."""
    chunks = _chunk_text(text, chunk_size, chunk_overlap)
    if not chunks:
        return 0

    metadata = [
        {"content": chunk, "file_id": file_id, "user_id": user_id, "chunk_index": i}
        for i, chunk in enumerate(chunks)
    ]

    client.add(
        collection_name=collection_name,
        documents=chunks,
        metadata=metadata,
    )
    return len(chunks)


def query(
    query_text: str,
    user_id: int,
    n_results: int = 5,
    collection_name: str = "documents",
) -> List[Dict]:
    """Query the vector store and return relevant chunks."""
    results = client.query(
        collection_name=collection_name,
        query_text=query_text,
        query_filter=Filter(
            must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]
        ),
        limit=n_results,
    )

    documents = []
    for point in results:
        documents.append({
            "content": point.metadata.get("content", ""),
            "metadata": {
                "file_id": point.metadata.get("file_id"),
                "user_id": point.metadata.get("user_id"),
                "chunk_index": point.metadata.get("chunk_index"),
            },
            "distance": point.score,
        })
    return documents


def delete_document(file_id: int, collection_name: str = "documents") -> None:
    """Remove all chunks for a file from the vector store."""
    client.delete(
        collection_name=collection_name,
        points_selector=Filter(
            must=[FieldCondition(key="file_id", match=MatchValue(value=file_id))]
        ),
    )


def _chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    """Split text into overlapping chunks."""
    if not text or not text.strip():
        return []

    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        start += chunk_size - overlap

    return chunks
