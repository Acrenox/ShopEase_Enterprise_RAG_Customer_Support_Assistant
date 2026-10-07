import json
from pathlib import Path

from langchain_core.documents import Document

from ingestion.document_cleaner import clean_text


def load_documents():
    documents = []
    raw_dir = Path('data/raw')

    with open('data/sources.json', encoding='utf-8') as handle:
        sources = json.load(handle)

    source_map = {item['source_id']: item for item in sources}

    for file in sorted(raw_dir.glob('*')):
        if not file.is_file():
            continue
        if file.suffix.lower() not in {'.txt', '.md'}:
            continue

        text = file.read_text(encoding='utf-8')
        cleaned_text = clean_text(text)
        source = source_map.get(file.stem, {})

        documents.append(
            Document(
                page_content=cleaned_text,
                metadata={
                    'document_id': file.stem,
                    'source': file.name,
                    'source_url': source.get('url'),
                    'category': source.get('category', 'general'),
                    'region': source.get('region', 'IN'),
                },
            )
        )

    return documents
