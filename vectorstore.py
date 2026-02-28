"""
vectorstore.py
Manages ChromaDB initialization, storage, and retrieval of embedded chunks.
"""

import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document


CHROMA_PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "sales_leads"


def get_embeddings() -> OpenAIEmbeddings:
    """Initialize OpenAI embeddings model."""
    return OpenAIEmbeddings(model="text-embedding-3-small")


def get_vectorstore(embeddings: Optional[OpenAIEmbeddings] = None) -> Chroma:
    """
    Load or create a persistent ChromaDB vectorstore.
    Returns existing store if already populated.
    """
    if embeddings is None:
        embeddings = get_embeddings()

    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_PERSIST_DIR,
    )
    return vectorstore


def add_documents_to_vectorstore(
    documents: List[Document],
    embeddings: Optional[OpenAIEmbeddings] = None,
) -> Chroma:
    """
    Embed and store a list of LangChain Documents into ChromaDB.
    Clears existing collection first to avoid duplicates on re-ingestion.
    """
    if embeddings is None:
        embeddings = get_embeddings()

    # Clear existing data so re-processing is idempotent
    if os.path.exists(CHROMA_PERSIST_DIR):
        client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass

    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_PERSIST_DIR,
    )
    return vectorstore


def similarity_search(
    query: str,
    vectorstore: Optional[Chroma] = None,
    k: int = 8,
) -> List[Document]:
    """
    Retrieve the top-k most relevant document chunks for a query.
    """
    if vectorstore is None:
        vectorstore = get_vectorstore()

    results = vectorstore.similarity_search(query, k=k)
    return results


def is_vectorstore_populated() -> bool:
    """Check whether the ChromaDB collection already has documents."""
    if not os.path.exists(CHROMA_PERSIST_DIR):
        return False
    try:
        client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        collection = client.get_collection(COLLECTION_NAME)
        return collection.count() > 0
    except Exception:
        return False


def get_all_lead_names(vectorstore: Optional[Chroma] = None) -> List[str]:
    """Extract unique lead names from stored chunk metadata."""
    if vectorstore is None:
        vectorstore = get_vectorstore()

    try:
        collection = vectorstore._collection
        results = collection.get(include=["metadatas"])
        names = set()
        for meta in results.get("metadatas", []):
            if meta and meta.get("lead_name") and meta["lead_name"] != "Unknown":
                names.add(meta["lead_name"])
        return sorted(list(names))
    except Exception:
        return []
