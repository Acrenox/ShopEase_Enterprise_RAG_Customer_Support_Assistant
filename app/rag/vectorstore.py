from __future__ import annotations

from pathlib import Path

from langchain_community.vectorstores import FAISS

from app.rag.embeddings import get_embeddings

INDEX_PATH = Path('vectorstore/faiss_index')


def create_vectorstore(documents):
    embeddings = get_embeddings()
    vectorstore = FAISS.from_documents(documents, embeddings)
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(INDEX_PATH))
    return vectorstore


def build_default_vectorstore():
    from ingestion.chunker import split_documents
    from ingestion.document_loader import load_documents

    documents = load_documents()
    chunks = split_documents(documents)
    return create_vectorstore(chunks)


def load_vectorstore():
    if not (INDEX_PATH / 'index.faiss').exists() or not (INDEX_PATH / 'index.pkl').exists():
        return build_default_vectorstore()

    embeddings = get_embeddings()
    return FAISS.load_local(str(INDEX_PATH), embeddings, allow_dangerous_deserialization=True)
