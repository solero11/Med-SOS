"""
Tamper-evident audit logging utilities.
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict

from src.security.deid import scrub_record

AUDIT_FILE = Path('_validation/audit_log.jsonl')
AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)


def append_audit(event: str, user: str, payload: Dict[str, Any]) -> None:
    payload = scrub_record(payload)
    last_hash = '0' * 64
    if AUDIT_FILE.exists():
        with AUDIT_FILE.open('r', encoding='utf-8') as handle:
            lines = handle.readlines()
            if lines:
                try:
                    last_hash = json.loads(lines[-1]).get('hash', last_hash)
                except json.JSONDecodeError:
                    pass
    entry = {
        'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'user': user,
        'event': event,
        'payload': payload,
        'prev_hash': last_hash,
    }
    digest = hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).hexdigest()
    entry['hash'] = digest
    with AUDIT_FILE.open('a', encoding='utf-8') as handle:
        handle.write(json.dumps(entry) + '\n')
