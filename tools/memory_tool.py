"""Long-term memory tool — ChromaDB read/write wrapper.

Embeds research reports with sentence-transformers and stores them in a local,
persistent ChromaDB collection. All functions degrade gracefully: if ChromaDB
or the embedding model is unavailable, reads return empty results and writes
become no-ops (with a logged warning), so the pipeline keeps running.
"""

import datetime
from typing import List, Optional

from utils.logger import get_logger

log = get_logger("memory_tool")

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "research_memory"
EMBED_MODEL = "all-MiniLM-L6-v2"

# Lazily-initialised singletons. We defer construction so that importing this
# module never fails just because the model files or DB aren't ready yet.
_client = None
_collection = None
_embedder = None


def _get_collection():
    """Return the Chroma collection, constructing it on first use."""
    global _client, _collection
    if _collection is None:
        import chromadb

        _client = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = _client.get_or_create_collection(COLLECTION_NAME)
    return _collection


def _get_embedder():
    """Return the sentence-transformers embedder, loading it on first use."""
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer

        _embedder = SentenceTransformer(EMBED_MODEL)
    return _embedder


def retrieve_past_research(query: str, n_results: int = 3) -> str:
    """Retrieve relevant past research for a query.

    Returns a formatted string of past findings, or an empty string if there is
    nothing relevant or memory is unavailable.
    """
    try:
        collection = _get_collection()
        # Nothing stored yet → skip the query entirely.
        if collection.count() == 0:
            return ""
        embedder = _get_embedder()
        embedding = embedder.encode(query).tolist()
        results = collection.query(
            query_embeddings=[embedding],
            n_results=min(n_results, collection.count()),
        )
    except Exception as exc:
        log.warning("ChromaDB retrieve failed (continuing without memory): %s", exc)
        return ""

    docs = results.get("documents") or []
    if not docs or not docs[0]:
        return ""
    return "\n\n---\n\n".join(docs[0])


def save_research(query: str, report: str, session_id: str) -> None:
    """Save a completed research report to ChromaDB (no-op on failure)."""
    try:
        collection = _get_collection()
        embedder = _get_embedder()
        embedding = embedder.encode(report[:2000]).tolist()
        collection.add(
            documents=[report],
            embeddings=[embedding],
            ids=[session_id],
            metadatas=[
                {
                    "query": query,
                    "timestamp": datetime.datetime.utcnow().isoformat(),
                }
            ],
        )
    except Exception as exc:
        log.warning("ChromaDB save failed (report not persisted): %s", exc)


def list_sessions() -> List[dict]:
    """Return metadata for every saved session, newest first.

    Used by the Streamlit sidebar to show past-session history. Returns a list
    of ``{id, query, timestamp, report}`` dicts.
    """
    try:
        collection = _get_collection()
        if collection.count() == 0:
            return []
        data = collection.get(include=["metadatas", "documents"])
    except Exception as exc:
        log.warning("ChromaDB list failed: %s", exc)
        return []

    ids = data.get("ids") or []
    metadatas = data.get("metadatas") or []
    documents = data.get("documents") or []

    sessions = []
    for i, _id in enumerate(ids):
        meta = metadatas[i] if i < len(metadatas) else {}
        doc = documents[i] if i < len(documents) else ""
        sessions.append(
            {
                "id": _id,
                "query": (meta or {}).get("query", "(unknown topic)"),
                "timestamp": (meta or {}).get("timestamp", ""),
                "report": doc,
            }
        )
    sessions.sort(key=lambda s: s["timestamp"], reverse=True)
    return sessions
