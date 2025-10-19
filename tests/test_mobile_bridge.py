from __future__ import annotations
import pytest

import asyncio
import statistics
from pathlib import Path

import aiohttp

TOKEN_PATH = Path("_validation/security/sos_token.txt")
SECURE_MODE = TOKEN_PATH.exists()
ORCH_URL = "https://127.0.0.1:8000" if SECURE_MODE else "http://127.0.0.1:8000"
ITERATIONS = 10


pytestmark = pytest.mark.asyncio


async def _turn_text(session: aiohttp.ClientSession, index: int, headers: dict[str, str]) -> float:
    start = asyncio.get_event_loop().time()
    async with session.post(f"{ORCH_URL}/turn_text", json={"text": f"Android ping {index}"}, headers=headers) as response:
        await response.text()
    return asyncio.get_event_loop().time() - start


async def test_android_pair():
    headers = {}
    connector = None
    if SECURE_MODE:
        token = TOKEN_PATH.read_text(encoding="utf-8").strip()
        headers["Authorization"] = f"Bearer {token}"
        connector = aiohttp.TCPConnector(ssl=False)

    lats = []
    async with aiohttp.ClientSession(connector=connector) as session:
        for i in range(ITERATIONS):
            try:
                latency = await _turn_text(session, i, headers)
            except aiohttp.ClientError as exc:
                raise AssertionError(f"/turn_text network failure at iteration {i}: {exc}") from exc
            lats.append(latency)
            await asyncio.sleep(0.3)

    mean = statistics.mean(lats)
    sorted_lats = sorted(lats)
    p95_index = max(0, min(len(sorted_lats) - 1, int(len(sorted_lats) * 0.95) - 1))
    p95 = sorted_lats[p95_index]
    print(f"Android bridge simulated mean={mean:.2f}s p95={p95:.2f}s secure={SECURE_MODE}")
    assert mean < 5.0 and p95 < 7.0
