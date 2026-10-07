from __future__ import annotations

from types import SimpleNamespace

from app.core.config import settings


class LocalLLM:
    def invoke(self, prompt: str | object):
        if hasattr(prompt, 'to_messages'):
            messages = prompt.to_messages()
            text = '\n'.join(getattr(m, 'content', str(m)) for m in messages)
        elif isinstance(prompt, str):
            text = prompt
        else:
            text = str(prompt)
        return SimpleNamespace(content=text.strip())


def get_llm():
    provider = settings.llm_provider.lower()

    if provider == 'local':
        return LocalLLM()

    if provider == 'azure':
        try:
            from langchain_openai import AzureChatOpenAI
        except ModuleNotFoundError as exc:
            raise RuntimeError('Azure OpenAI dependencies are not installed. Install langchain-openai or switch LLM_PROVIDER=local.') from exc

        return AzureChatOpenAI(
            azure_deployment=settings.azure_openai_chat_deployment or 'gpt-4o-mini',
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            temperature=0,
        )

    if provider == 'gemini':
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except ModuleNotFoundError as exc:
            raise RuntimeError('Gemini dependencies are not installed. Install langchain-google-genai or switch LLM_PROVIDER=local.') from exc

        return ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.google_api_key,
            temperature=0,
        )

    raise ValueError(f'Unsupported LLM provider: {provider}')
