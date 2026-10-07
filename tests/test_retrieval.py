from app.rag.retriever import retrieve


def test_retrieval_returns_results():
    results = retrieve('How can I track my order?', category='shipping')
    assert isinstance(results, list)
    assert len(results) >= 1
    assert all('document' in item for item in results)


def test_retrieval_without_category_works():
    results = retrieve('How do I cancel my order?')
    assert isinstance(results, list)
    assert len(results) >= 1
