"""
Lightweight runtime wrapper for interacting with LM Studio's chat completions API.

The helper intentionally focuses on the subset of functionality needed by the
SBAR chaos harness so it can run locally without additional infrastructure.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Dict, Optional, Sequence

import requests


def _default_api_url() -> str:
    return os.environ.get("LLM_API_URL", "http://127.0.0.1:1234/v1/chat/completions")


def _default_model() -> str:
    return os.environ.get("LM_STUDIO_MODEL", "medicine-llm-13b")


def _default_timeout() -> int:
    raw = os.environ.get("LM_STUDIO_TIMEOUT", "30")
    try:
        return max(5, int(raw))
    except ValueError:
        return 30


def _normalise_chat_url(base_url: str) -> str:
    url = base_url.rstrip("/")
    if url.endswith("/chat/completions"):
        return url
    if url.endswith("/v1"):
        return f"{url}/chat/completions"
    if "/v1/chat/completions" in url:
        return url.split("?")[0]
    return f"{url}/v1/chat/completions"


def _models_endpoint(chat_url: str) -> str:
    root = chat_url
    marker = "/v1/chat/completions"
    if marker in root:
        root = root[: root.index(marker)]
    root = root.rstrip("/")
    if not root.endswith("/v1"):
        root = f"{root}/v1"
    return f"{root}/models"


def _extract_token_count(payload: Dict) -> int:
    usage = payload.get("usage")
    if isinstance(usage, dict):
        for key in ("total_tokens", "completion_tokens", "input_tokens", "prompt_tokens"):
            value = usage.get(key)
            if isinstance(value, int):
                return int(value)
    meta = payload.get("meta")
    if isinstance(meta, dict):
        for key in ("total_tokens", "tokens"):
            value = meta.get(key)
            if isinstance(value, int):
                return int(value)
    return 0


@dataclass
class LMStudioRuntime:
    """
    Minimal runtime client that mirrors the subset of the OpenAI Chat API exposed by LM Studio.
    """

    base_url: str = _default_api_url()
    model: str = _default_model()
    timeout: int = _default_timeout()

    def __post_init__(self) -> None:
        self._chat_url = _normalise_chat_url(self.base_url)
        self._models_url = _models_endpoint(self._chat_url)

    def is_available(self) -> bool:
        """
        Best-effort probe to determine whether LM Studio is reachable.
        """
        try:
            response = requests.get(self._models_url, timeout=min(self.timeout, 5))
            if response.ok or response.status_code in (401, 403):
                return True
        except requests.RequestException:
            pass

        # Fallback: issue a lightweight chat request since some builds do not expose /v1/models.
        probe_payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": "ping"}],
            "max_tokens": 1,
            "stream": False,
            "temperature": 0.0,
        }
        try:
            response = requests.post(self._chat_url, json=probe_payload, timeout=min(self.timeout, 5))
            return response.ok
        except requests.RequestException:
            return False

    def chat(
        self,
        messages: Sequence[Dict[str, str]],
        *,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        model: Optional[str] = None,
        response_format: Optional[Dict[str, object]] = None,
    ) -> Dict[str, object]:
        """
        Issue a chat completion request and return the parsed response plus basic telemetry.
        """
        payload: Dict[str, object] = {
            "model": model or self.model,
            "messages": list(messages),
            "temperature": float(temperature),
            "stream": bool(stream),
        }
        if max_tokens is not None:
            payload["max_tokens"] = int(max_tokens)
        if response_format:
            payload["response_format"] = response_format

        start = time.perf_counter()
        response = requests.post(self._chat_url, json=payload, timeout=self.timeout)
        latency = time.perf_counter() - start
        response.raise_for_status()
        data: Dict = response.json() if response.content else {}

        content = ""
        if isinstance(data, dict):
            choices = data.get("choices")
            if isinstance(choices, list) and choices:
                first = choices[0] or {}
                message = first.get("message")
                if isinstance(message, dict):
                    content = message.get("content", "") or ""

        return {
            "content": content.strip(),
            "usage": data.get("usage") if isinstance(data, dict) else None,
            "tokens": _extract_token_count(data) if isinstance(data, dict) else 0,
            "latency": latency,
            "raw": data,
        }


__all__ = ["LMStudioRuntime"]
