from __future__ import annotations

import json
import time
from pathlib import Path

from fastapi.testclient import TestClient

from src.orchestrator.app import create_app

METRICS_PATH = Path('_validation/orchestrator_metrics.jsonl')
TOKEN_PATH = Path('_validation/security/sos_token.txt')


def test_dashboard_websocket_stream():
    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_PATH.write_text('test-admin-token', encoding='utf-8')
    METRICS_PATH.write_text(json.dumps({'event': 'turn_text', 'ok': True}) + '
', encoding='utf-8')

    app = create_app()
    client = TestClient(app)
    with client.websocket_connect('/ws/metrics?token=test-admin-token') as websocket:
        with METRICS_PATH.open('a', encoding='utf-8') as handle:
            handle.write(json.dumps({'event': 'turn_audio', 'ok': True}) + '
')
        time.sleep(1.1)
        message = websocket.receive_text()
        payload = json.loads(message)
        assert payload['event'] in {'turn_text', 'turn_audio'}

    METRICS_PATH.unlink(missing_ok=True)
