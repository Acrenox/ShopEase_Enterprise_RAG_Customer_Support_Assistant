from __future__ import annotations

from app.core.config import settings
from app.rag.generator import generate_answer
from app.rag.query_rewriter import rewrite_query
from app.rag.query_router import detect_category
from app.rag.reranker import rerank
from app.rag.retriever import retrieve


class RAGPipeline:
    def ask(self, question: str, history=None):
        category = detect_category(question)
        rewritten_question = rewrite_query(question, history)
        results = retrieve(rewritten_question, category)

        if not results:
            return {
                'answer': "I don't have enough information to answer that question confidently.",
                'sources': [],
                'category': category,
                'confidence': 0.0,
                'escalation_required': True,
            }

        ranked_results = rerank(results)[: settings.final_k]
        answer = generate_answer(rewritten_question, ranked_results, category=category)

        sources = []
        for item in ranked_results:
            metadata = item['document'].metadata
            sources.append(
                {
                    'document': metadata.get('document_id', 'unknown'),
                    'category': metadata.get('category', 'general'),
                    'url': metadata.get('source_url'),
                }
            )

        return {
            'answer': answer,
            'sources': sources,
            'category': category,
            'confidence': 0.8,
            'escalation_required': False,
        }
