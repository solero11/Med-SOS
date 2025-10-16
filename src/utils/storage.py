"""
Object storage helpers for validation artifacts.
"""

from __future__ import annotations

import os
import pathlib

try:
    import boto3
except ImportError:  # pragma: no cover
    boto3 = None

_s3 = None
_BUCKET = os.getenv("VALIDATION_BUCKET")
_REGION = os.getenv("AWS_REGION")


def _client():
    global _s3
    if _s3 is None:
        if not _BUCKET or boto3 is None:
            raise RuntimeError("Object storage not configured")
        _s3 = boto3.client("s3", region_name=_REGION)
    return _s3


def upload_validation_file(local_path: pathlib.Path) -> str:
    client = _client()
    key = f"validation/{local_path.name}"
    client.upload_file(str(local_path), _BUCKET, key)
    return f"s3://{_BUCKET}/{key}"
