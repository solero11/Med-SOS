import os

import pytest
import requests

ASR_API_URL = os.getenv("ASR_API_URL", "http://127.0.0.1:9001")


@pytest.fixture(scope="session", autouse=True)
def ensure_asr_ready():
    """
    Fail fast when the real ASR service is not available.
    """
    ready_url = f"{ASR_API_URL.rstrip('/')}/ready"
    try:
        response = requests.get(ready_url, timeout=5)
    except requests.RequestException as exc:
        pytest.exit(
            f"ASR service unavailable on {ready_url} — start rtc-gateway + asr_api before running tests. "
            f"Original error: {exc}",
            returncode=2,
        )
    if response.status_code != 200:
        pytest.exit(
            f"ASR service reported {response.status_code} on {ready_url}. "
            "Start rtc-gateway + asr_api before running tests.",
            returncode=2,
        )
