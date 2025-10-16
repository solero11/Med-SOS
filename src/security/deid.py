"""
PHI de-identification helpers.
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict

PHI_PATTERNS = [
    (r"\b\d{3}-\d{2}-\d{4}\b", "[SSN]"),
    (r"\b\d{3}-\d{3}-\d{4}\b", "[PHONE]"),
    (r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", "[DATE]"),
    (r"\b([A-Z][a-z]+ ){1,3}[A-Z][a-z]+\b", "[NAME]")
]

def scrub(text: str) -> str:
    if not text:
        return text
    for pattern, repl in PHI_PATTERNS:
        text = re.sub(pattern, repl, text)
    return text


def scrub_record(record: Dict[str, Any]) -> Dict[str, Any]:
    serialized = json.dumps(record)
    cleaned = re.sub(r'"([^"\\]|\\.)*"', lambda m: scrub(m.group(0)), serialized)
    return json.loads(cleaned)
