"""
Pairing helpers (token + QR) for mobile/desktop linking.
"""
from __future__ import annotations

import base64
import io
import secrets
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request

from src.security.auth import issue_token, verify_token
from src.utils.audit_logger import append_audit
from src.utils.logger import log_turn_metric

try:
    import qrcode
except ImportError:  # pragma: no cover - optional dependency
    qrcode = None

router = APIRouter()
SECURITY_TOKEN_PATH = Path('_validation/security/sos_token.txt')


def _admin_guard(request: Request):
    header = request.headers.get('Authorization', '').replace('Bearer ', '').strip()
    if not header:
        raise HTTPException(status_code=401, detail='Unauthorized')
    try:
        data = verify_token(header, roles=['admin'])
    except Exception:
        expected = SECURITY_TOKEN_PATH.read_text(encoding='utf-8').strip() if SECURITY_TOKEN_PATH.exists() else ''
        if header != expected:
            raise HTTPException(status_code=401, detail='Unauthorized')
        data = {'sub': 'bootstrap', 'role': 'admin'}
    request.state.user = data
    return data


def _make_qr_png(payload: str) -> Optional[str]:
    if qrcode is None:
        return None
    img = qrcode.make(payload)
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    encoded = base64.b64encode(buffer.getvalue()).decode()
    return f'data:image/png;base64,{encoded}'


@router.get('/pair')
async def create_pairing_token(request: Request, user=Depends(_admin_guard)):
    token_id = secrets.token_urlsafe(12)
    jwt_token = issue_token(user=token_id, role='clinician', ttl_seconds=3600)
    qr_payload = f'sos://pair?token={jwt_token}'
    payload = {'token': jwt_token, 'uri': qr_payload}
    qr_data = _make_qr_png(qr_payload)
    if qr_data:
        payload['qr_png'] = qr_data
    log_turn_metric('pair_request', True, 0.0, {'secure': True})
    append_audit('pair_request', user.get('sub', 'admin'), {'token_id': token_id})
    return payload
