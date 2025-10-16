"""
JWT token issuance and verification helpers.
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Optional

import jwt

SECRET = os.getenv('TOKEN_SECRET', 'change-me')
ALGORITHM = 'HS256'


def issue_token(user: str, role: str = 'clinician', ttl_seconds: int = 3600) -> str:
    payload = {
        'sub': user,
        'role': role,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(seconds=ttl_seconds),
    }
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)


def verify_token(token: str, roles: Optional[list[str]] = None) -> dict:
    data = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
    if roles and data.get('role') not in roles:
        raise PermissionError('insufficient role')
    return data
