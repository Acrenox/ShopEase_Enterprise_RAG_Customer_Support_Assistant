from __future__ import annotations

from app.core.config import settings
from app.rag.vectorstore import load_vectorstore
from ingestion.document_loader import load_documents

CATEGORY_KEYWORDS = {
    'shipping': ['shipping', 'delivery', 'shipment', 'track', 'tracking', 'parcel', 'courier'],
    'returns': ['return', 'returns', 'damaged', 'defective', 'incorrect', 'exchange'],
    'refunds': ['refund', 'refunds', 'reimbursement', 'money back', 'payment'],
    'cancellation': ['cancel', 'cancellation', 'cancelled', 'withdraw'],
    'warranty': ['warranty', 'guarantee', 'repair', 'faulty', 'defective'],
    'product': ['product', 'price', 'availability', 'stock', 'specification'],
}


def retrieve(question: str, category: str | None = None):
    vectorstore = load_vectorstore()
    results = vectorstore.similarity_search_with_score(question, k=settings.top_k)

    documents: list[dict] = []
    for document, score in results:
        if category:
            document_category = document.metadata.get('category')
            if document_category != category and category != 'general':
                continue
        documents.append({'document': document, 'score': float(score)})

    if category and not documents:
        keyword_tokens = CATEGORY_KEYWORDS.get(category, [])
        combined_matches = []

        for document, score in results:
            content = document.page_content.lower()
            is_exact_category = document.metadata.get('category') == category
            if is_exact_category or any(token in content for token in keyword_tokens):
                combined_matches.append({'document': document, 'score': (2.0 if is_exact_category else 1.0) + float(score)})

        for document in load_documents():
            content = document.page_content.lower()
            metadata_category = document.metadata.get('category')
            is_exact_category = metadata_category == category
            if is_exact_category or any(token in content for token in keyword_tokens):
                combined_matches.append({'document': document, 'score': (4.0 if is_exact_category else 2.0)})

        if combined_matches:
            deduped = {}
            for match in combined_matches:
                key = match['document'].metadata.get('source')
                deduped[key] = match
            return sorted(deduped.values(), key=lambda item: item['score'], reverse=True)[: settings.final_k]

        return [
            {'document': document, 'score': float(score)}
            for document, score in results[: settings.final_k]
        ]

    return documents
