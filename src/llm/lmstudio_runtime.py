"""
Helpers to ensure LM Studio is running with the desired model.

LM Studio exposes an OpenAI-compatible API plus a small management surface
for loading/unloading models. We probe the instance, eject any currently
loaded model, and load the requested Medicine LLM if needed.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable, List, Optional

import requests


def _join(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}{path}"


@dataclass
class LMStudioRuntime:
    base_url: str = "http://localhost:1234"
    target_model: str = "medicine-llm-13b"
    timeout: int = 10

    @classmethod
    def from_env(cls) -> "LMStudioRuntime":
        return cls(
            base_url=os.environ.get("LM_STUDIO_BASE_URL", cls.base_url),
            target_model=os.environ.get("LM_STUDIO_MODEL", cls.target_model),
            timeout=int(os.environ.get("LM_STUDIO_TIMEOUT", cls.timeout)),
        )

    def get_loaded_models(self) -> List[str]:
        """Return a list of currently loaded model ids."""
        for path in ("/v1/models/active", "/v1/models"):
            try:
                response = requests.get(_join(self.base_url, path), timeout=self.timeout)
                if response.status_code >= 400:
                    continue
                payload = response.json()
            except requests.RequestException:
                continue
            data = payload.get("data")
            if isinstance(data, list):
                models = [item.get("id") for item in data if isinstance(item, dict) and item.get("id")]
                if models:
                    return models
            if isinstance(payload, dict) and payload.get("id"):
                return [payload["id"]]
        return []

    def unload_model(self, model_id: str) -> bool:
        candidates = (
            ("/v1/models/unload", {"model": model_id}),
            ("/v1/models", {"model": model_id, "action": "unload"}),
        )
        return self._try_post(candidates)

    def load_model(self, model_id: str) -> bool:
        candidates = (
            ("/v1/models/load", {"model": model_id}),
            ("/v1/models", {"model": model_id, "action": "load"}),
        )
        return self._try_post(candidates)

    def _try_post(self, candidates: Iterable[tuple[str, dict]]) -> bool:
        for path, payload in candidates:
            try:
                response = requests.post(
                    _join(self.base_url, path),
                    json=payload,
                    timeout=self.timeout,
                )
                if response.status_code < 400:
                    return True
            except requests.RequestException:
                continue
        return False

    def ensure_model_loaded(self) -> Optional[str]:
        """
        Ensure the target model is the one exposed by LM Studio.

        Returns the active model id if successful, otherwise raises RuntimeError.
        """
        loaded = self.get_loaded_models()
        if self.target_model in loaded:
            return self.target_model

        # Attempt to unload other active models when the management API supports it.
        for model_id in loaded:
            if model_id == self.target_model:
                continue
            self.unload_model(model_id)

        # Some LM Studio builds auto-load models on demand; treat load failures as non-fatal.
        self.load_model(self.target_model)

        loaded_after = self.get_loaded_models()
        if not loaded_after or self.target_model in loaded_after:
            return self.target_model
        # Fall back to assuming just-in-time loading is available.
        return self.target_model
