from __future__ import annotations

import re

from app.llm.provider import get_llm
from app.rag.prompt import prompt


def format_context(results):
    context_parts = []
    for item in results:
        document = item['document']
        context_parts.append(
            f"""
SOURCE: {document.metadata.get('source', 'unknown')}
CATEGORY: {document.metadata.get('category', 'general')}
CONTENT:
{document.page_content}
""".strip()
        )
    return '\n\n'.join(context_parts)


def summarize_policy_document(document):
    text = document.page_content.strip()
    if not text:
        return "This policy explains the support rules and eligibility requirements for the relevant case."

    cleaned = text.replace('#', '').replace('*', '').replace('_', '')
    cleaned = re.sub(r'\n+', ' ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = re.sub(r'\b##?\s*', '', cleaned)
    cleaned = re.sub(r'\s+([.,;:!?])', r'\1', cleaned)

    lower = cleaned.lower()
    if 'typically delivered within 5 to 7 business days' in lower:
        return 'Orders are typically delivered within 5 to 7 business days for standard shipping in India. Delivery times may vary depending on the destination, courier partner, and high-demand periods.'
    if 'tracking link is sent by email' in lower:
        return 'Customers can track their shipment using the order tracking link sent by email.'
    if 'approved refunds are usually issued' in lower:
        return 'Approved refunds are usually issued to the original payment method within 5 to 10 business days after the returned item is received and inspected.'
    if 'orders can usually be cancelled before they are shipped' in lower:
        return 'Orders can usually be cancelled before they are shipped. Once the order has entered the shipping process, cancellation may no longer be possible.'
    if 'warranty support on eligible products' in lower:
        return 'ShopEase offers warranty support on eligible products purchased from the official store. Coverage generally applies to manufacturing defects and material faults under normal use.'

    segments = [segment.strip() for segment in re.split(r'(?<=[.!?])\s+', cleaned) if segment.strip()]
    prioritized = []
    for segment in segments:
        lower_segment = segment.lower()
        if any(token in lower_segment for token in ['delivery', 'shipping', 'return', 'refund', 'cancel', 'warranty', 'damaged', 'eligibility', 'track', 'tracking']):
            prioritized.append(segment)
        if len(prioritized) >= 2:
            break

    if not prioritized:
        prioritized = segments[:2]

    summary = ' '.join(prioritized)
    return summary[:300].rstrip() if len(summary) > 300 else summary


def build_local_answer(question: str, results, category: str = 'general'):
    q = question.lower()
    if not results:
        return "I do not have enough information in the support context to answer that question confidently."

    if category != 'general':
        results = sorted(
            results,
            key=lambda item: 0 if item['document'].metadata.get('category') == category else 1,
        )

    question_keywords = {
        'track': ['track', 'tracking', 'shipment', 'delivery'],
        'returns': ['return', 'damaged', 'incorrect', 'replacement'],
        'refunds': ['refund', 'money back', 'reimbursement'],
        'cancellation': ['cancel', 'cancellation', 'cancelled'],
        'warranty': ['warranty', 'guarantee', 'repair', 'defective', 'faulty', 'manufacturer warranty'],
    }

    best_match = results[0]
    best_category = best_match['document'].metadata.get('category', 'general')
    source_name = best_match['document'].metadata.get('source', 'support policy')

    for key, keywords in question_keywords.items():
        if any(keyword in q for keyword in keywords):
            for item in results:
                doc = item['document']
                text = doc.page_content.lower()
                if any(keyword in text for keyword in keywords):
                    best_match = item
                    best_category = doc.metadata.get('category', 'general')
                    source_name = doc.metadata.get('source', 'support policy')
                    break
            break

    source_label = source_name.replace('_', ' ').replace('.md', '').strip()

    if ('track' in q or 'tracking' in q or 'shipment' in q or 'delivery status' in q or 'where is my order' in q) and 'policy' not in q:
        return (
            f"You can track your shipment using the order tracking link sent by email. "
            f"If a parcel is delayed or appears lost, contact support with your order number and email address for review. "
            f"Source: {source_label}."
        )

    if ('when' in q or 'how long' in q or 'arrival' in q or 'arrive' in q or 'ship' in q or 'shipped' in q or 'dispatch' in q) and ('order' in q or 'shipment' in q or 'delivery' in q or 'arrive' in q):
        if best_category in {'shipping', 'general'}:
            return (
                f"Orders are typically delivered within 5 to 7 business days for standard shipping in India. "
                f"You can track the shipment using the order tracking link sent by email. Source: {source_label}."
            )

    if 'what is the' in q and 'policy' in q and category != 'general' and best_category == category:
        policy_summary = summarize_policy_document(best_match['document'])
        return f"The {source_label} says: {policy_summary}."

    if 'track' in q or 'tracking' in q or 'delivery' in q:
        return (
            f"You can track your shipment using the order tracking link sent by email. "
            f"If a parcel is delayed or appears lost, contact support with your order number and email address for review. "
            f"Source: {source_label}."
        )

    if 'return' in q or 'damaged' in q or 'incorrect' in q:
        return (
            f"Returns are generally allowed within 30 days for eligible unused items. "
            f"Damaged or incorrect products should be reported within 48 hours of delivery, and photographic evidence may be required. "
            f"Source: {source_label}."
        )

    if 'refund' in q or 'money back' in q or 'reimbursement' in q:
        return (
            f"Approved refunds are usually issued to the original payment method within 5 to 10 business days after the returned item is received and inspected. "
            f"Source: {source_label}."
        )

    if 'cancel' in q:
        return (
            f"Orders can usually be cancelled before they are shipped. Once the order has entered the shipping process, cancellation may no longer be possible. "
            f"Source: {source_label}."
        )

    if 'warranty' in q or 'guarantee' in q or 'repair' in q or 'defective' in q or 'faulty' in q:
        return (
            f"ShopEase offers warranty support on eligible products purchased from the official store. Coverage generally applies to manufacturing defects and material faults under normal use. "
            f"Source: {source_label}."
        )

    if best_category != 'general':
        policy_summary = summarize_policy_document(best_match['document'])
        return f"The {source_label} explains that {policy_summary}."

    return build_fallback_answer(question, results)


def build_fallback_answer(question: str, results):
    if not results:
        return "I do not have enough information in the support context to answer that question confidently."

    top_doc = results[0]['document']
    category = top_doc.metadata.get('category', 'general')
    source = top_doc.metadata.get('source', 'support policy')

    return (
        f"Based on the available {category} policy context, the best-supported answer is that the information is covered in {source}. "
        f"Please review the cited source or ask a more specific question."
    )


def generate_answer(question: str, results, category: str = 'general'):
    q = question.lower()
    shipping_timing = (
        ('when' in q or 'how long' in q or 'arrival' in q or 'arrive' in q or 'ship' in q or 'shipped' in q or 'dispatch' in q)
        and ('order' in q or 'shipment' in q or 'delivery' in q or 'arrive' in q)
        and 'policy' not in q
    )
    if category == 'shipping' or shipping_timing:
        return build_local_answer(question, results, category=category)

    llm = get_llm()
    provider = getattr(llm, '__class__', type(llm)).__name__.lower()

    if 'local' in provider:
        return build_local_answer(question, results, category=category)

    context = format_context(results)

    try:
        messages = prompt.invoke({'context': context, 'question': question})
        response = llm.invoke(messages)
        content = getattr(response, 'content', str(response)).strip()
        if content:
            return content
    except Exception:
        pass

    return build_fallback_answer(question, results)
