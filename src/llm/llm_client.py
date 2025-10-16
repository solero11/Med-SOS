"""
LLM Client Module

Handles communication with the local LLM via LM Studio's chat completions API.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Iterable, List, Optional

import requests
from requests.exceptions import HTTPError


class LLMClient:
    def __init__(
        self,
        api_url: str,
        system_prompt: str,
        model: str = "medicine-llm-13b",
        temperature: float = 0.7,
        max_tokens: int = -1,
        stream: bool = False,
    ):
        self.api_url = api_url
        self.system_prompt = system_prompt
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.stream = stream

    def ask(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
        history: Optional[Iterable[Dict[str, str]]] = None,
    ) -> str:
        """
        Send a user utterance to the LLM and return the assistant response.

        Args:
            user_input: Latest user utterance.
            context: Optional structured context inserted as a system message.
            history: Prior messages (list of {"role": "...", "content": "..."}).
        """
        messages: List[Dict[str, str]] = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        if context:
            context_text = json.dumps(context, ensure_ascii=False, indent=2)
            messages.append({"role": "system", "content": f"Context:\n{context_text}"})
        if history:
            for msg in history:
                if "role" in msg and "content" in msg:
                    messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": user_input})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "stream": self.stream,
        }
        if self.max_tokens is not None and self.max_tokens >= 0:
            payload["max_tokens"] = self.max_tokens
        response = requests.post(self.api_url, json=payload, timeout=60)
        try:
            response.raise_for_status()
        except HTTPError as exc:
            raise HTTPError(f"{exc} | Response body: {response.text}") from exc
        data = response.json()
        if "choices" in data and data["choices"]:
            return data["choices"][0]["message"]["content"]
        return data.get("response", "")
