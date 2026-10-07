from app.rag.pipeline import RAGPipeline


def test_pipeline_answer_generation():
    pipeline = RAGPipeline()
    result = pipeline.ask('Can I return a damaged product?')
    assert 'answer' in result
    assert isinstance(result['sources'], list)
    assert result['category'] in {'returns', 'shipping', 'refunds', 'cancellation', 'product', 'general'}
    assert result['confidence'] >= 0.0


def test_warranty_question_routes_to_warranty_policy():
    pipeline = RAGPipeline()
    result = pipeline.ask('What is the warranty policy?')
    assert result['category'] == 'warranty'
    assert 'warranty' in result['answer'].lower()


def test_shipping_policy_question_is_answered_from_policy_summary():
    pipeline = RAGPipeline()
    result = pipeline.ask('what is the shipping policy?')
    assert result['category'] == 'shipping'
    assert 'shipping policy' in result['answer'].lower()
    assert 'delivery' in result['answer'].lower() or 'tracking' in result['answer'].lower()


def test_shipment_status_question_uses_tracking_guidance():
    pipeline = RAGPipeline()
    result = pipeline.ask('What is the shipment of this order?')
    assert result['category'] == 'shipping'
    assert 'track' in result['answer'].lower() or 'tracking' in result['answer'].lower()
    assert 'the shipping policy states' not in result['answer'].lower()


def test_shipping_timing_question_routes_to_shipping_and_uses_delivery_timeline():
    pipeline = RAGPipeline()
    result = pipeline.ask('when will this order shipped?')
    assert result['category'] == 'shipping'
    assert '5 to 7 business days' in result['answer'] or 'business day' in result['answer'].lower()
    assert 'cancellation' not in result['answer'].lower()


def test_return_policy_question_uses_return_context_when_category_filter_is_empty():
    pipeline = RAGPipeline()
    result = pipeline.ask('what is the return policy?')
    assert result['category'] == 'returns'
    assert result['sources']
    assert any('return_policy' in source.lower() for source in [s['document'] for s in result['sources']])
