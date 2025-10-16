import asyncio
import os
import statistics
import time

import httpx
import pytest

ORCH_URL = os.getenv("ORCH_API_URL", "http://127.0.0.1:8000")
ITERATIONS = int(os.getenv("STRESS_ITERS", "10"))
WAV_PATH = os.getenv("STRESS_WAV_PATH", "_validation/test_ping.wav")


async def _turn_text(index: int) -> float:
    payload = {"text": f"Trial {index}: BP 80/40, HR 130. Next action?"}
    async with httpx.AsyncClient(timeout=15) as client:
        start = time.time()
        response = await client.post(f"{ORCH_URL}/turn_text", json=payload)
        latency = time.time() - start
    assert response.status_code == 200, f"/turn_text #{index} failed: {response.text}"
    return latency


@pytest.mark.asyncio
async def test_stress_recovery_turn_text():
    """Run multiple /turn_text calls to assess latency stability."""
    latencies = []
    for i in range(ITERATIONS):
        latencies.append(await _turn_text(i))
        await asyncio.sleep(0.5)
    mean = statistics.mean(latencies)
    p95 = sorted(latencies)[max(0, int(0.95 * len(latencies)) - 1)]
    print(f"/turn_text mean={mean:.2f}s p95={p95:.2f}s (n={len(latencies)})")
    assert mean < 5.0 and p95 < 7.0


@pytest.mark.asyncio
async def test_stress_recovery_turn_audio():
    """Alternate /turn audio calls to confirm ASR/TTS path stability."""
    assert os.path.exists(WAV_PATH), "generate test WAV first (tools/make_test_wav.py)"
    latencies = []
    audio_iterations = max(1, ITERATIONS // 2)
    for i in range(audio_iterations):
        async with httpx.AsyncClient(timeout=30) as client, open(WAV_PATH, "rb") as handle:
            start = time.time()
            response = await client.post(
                f"{ORCH_URL}/turn",
                files={"audio": ("stress.wav", handle, "audio/wav")},
            )
            latency = time.time() - start
        assert response.status_code == 200, f"/turn #{i} failed: {response.text}"
        latencies.append(latency)
        await asyncio.sleep(1.0)
    mean = statistics.mean(latencies)
    p95 = sorted(latencies)[max(0, int(0.95 * len(latencies)) - 1)]
    print(f"/turn mean={mean:.2f}s p95={p95:.2f}s (n={len(latencies)})")
    assert mean < 10.0 and p95 < 15.0
