from pathlib import Path


def create_metadata(file_path: Path, category: str, source_url: str):
    return {
        'document_id': file_path.stem,
        'source': file_path.name,
        'source_url': source_url,
        'category': category,
        'region': 'IN',
        'language': 'en',
        'document_type': 'customer_support',
    }
