from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_redirect_or_status():
    response = client.get('/')
    assert response.status_code in {200, 307, 308}


def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'healthy'


def test_chat_route():
    response = client.post('/api/v1/chat', json={'question': 'Can I return a damaged product?'})
    assert response.status_code == 200
    payload = response.json()
    assert 'answer' in payload
    assert 'sources' in payload
    assert 'category' in payload
    assert payload['category'] in {'returns', 'shipping', 'refunds', 'cancellation', 'product', 'general'}
