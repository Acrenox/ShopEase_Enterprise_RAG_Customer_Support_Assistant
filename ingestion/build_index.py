from ingestion.chunker import split_documents
from ingestion.document_loader import load_documents
from app.rag.vectorstore import create_vectorstore


def main():
    documents = load_documents()
    chunks = split_documents(documents)
    create_vectorstore(chunks)
    print(f'Loaded {len(documents)} documents and built {len(chunks)} chunks.')


if __name__ == '__main__':
    main()
