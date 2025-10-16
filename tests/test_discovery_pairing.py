from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from src.orchestrator.app import create_app


def test_pair_endpoint_returns_token_and_qr():
    token_path = Path('_validation/security/sos_token.txt')
    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text('test-admin-token', encoding='utf-8')
    app = create_app()
    client = TestClient(app)
    response = client.get('/pair', headers={'Authorization': 'Bearer test-admin-token'})
    assert response.status_code == 200
    data = response.json()
    assert 'token' in data and data['token']
    if 'qr_png' in data:
        assert data['qr_png'].startswith('data:image/png;base64,')
