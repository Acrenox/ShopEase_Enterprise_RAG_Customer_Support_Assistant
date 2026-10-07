from __future__ import annotations

from app.llm.provider import get_llm


def rewrite_query(question: str, history: list[dict] | None = None) -> str:
    if not history:
        return question

    llm = get_llm()
    conversation = '\n'.join(f"{entry.get('role', 'user')}: {entry.get('content', '')}" for entry in history)
    prompt = f"""
Rewrite the latest customer question into a standalone question.

Conversation:
{conversation}

Latest question:
{question}

Return only the rewritten question.
""".strip()
    response = llm.invoke(prompt)
    return getattr(response, 'content', str(response)).strip() or question
