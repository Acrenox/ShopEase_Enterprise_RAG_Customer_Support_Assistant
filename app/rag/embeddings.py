from __future__ import annotations

import hashlib
from typing import List

import numpy as np
from langchain_core.embeddings import Embeddings

from app.core.config import settings


class LocalEmbeddings(Embeddings):
    """Deterministic embeddings for offline local development and tests."""

    def __init__(self, dimensions: int = 32):
        self.dimensions = dimensions

    def _vector_for_text(self, text: str) -> np.ndarray:
        digest = hashlib.sha256(text.encode('utf-8')).hexdigest()
        seed = int(digest[:16], 16)
        rng = np.random.default_rng(seed)
        vector = rng.normal(0, 1, self.dimensions).astype('float32')
        return vector / np.linalg.norm(vector)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._vector_for_text(text).tolist() for text in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._vector_for_text(text).tolist()


def get_embeddings():
    provider = settings.llm_provider.lower()

    if provider == 'local':
        return LocalEmbeddings()

    if provider == 'azure':
        try:
            from langchain_openai import AzureOpenAIEmbeddings
        except ModuleNotFoundError as exc:
            raise RuntimeError('Azure OpenAI embedding dependencies are not installed. Install langchain-openai or switch LLM_PROVIDER=local.') from exc

        return AzureOpenAIEmbeddings(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_deployment=settings.azure_openai_embedding_deployment or 'text-embedding-3-small',
        )

    if provider == 'gemini':
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
        except ModuleNotFoundError as exc:
            raise RuntimeError('Gemini embedding dependencies are not installed. Install langchain-google-genai or switch LLM_PROVIDER=local.') from exc

        return GoogleGenerativeAIEmbeddings(
            model=settings.gemini_embedding_model or 'models/text-embedding-004',
            google_api_key=settings.google_api_key,
        )

    raise ValueError(f'Unsupported provider: {provider}')
