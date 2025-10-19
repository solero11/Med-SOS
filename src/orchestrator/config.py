"""
Environment-driven configuration helpers for the SOS orchestrator.
"""

import os
from pathlib import Path

ASR_API_URL = os.getenv("ASR_API_URL", "http://127.0.0.1:9001")
KOKORO_API_URL = os.getenv("KOKORO_API_URL", "http://127.0.0.1:8880")
USE_LOCAL_LLM = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
VALIDATION_BUCKET = os.getenv("VALIDATION_BUCKET")
ORCH_ENV = os.getenv("ORCH_ENV", "local")
LLM_MODE = os.getenv("LLM_MODE", "local").lower()
LM_LOCAL_URL = "http://100.111.223.74:1234/v1/chat/completions"
LLM_OLLAMA_URL = os.getenv("LLM_OLLAMA_URL", "http://127.0.0.1:11434/v1/chat/completions")
DEFAULT_LLM_URL = "http://100.111.223.74:1234/v1/chat/completions"

LLM_API_URL = os.getenv("LLM_API_URL") or (LM_LOCAL_URL if USE_LOCAL_LLM else DEFAULT_LLM_URL)
ORCHESTRATOR_AUDIO_DIR = Path(os.getenv("ORCHESTRATOR_AUDIO_DIR", "_validation/orchestrator_audio")).resolve()
HTTP_TIMEOUT = float(os.getenv("ORCHESTRATOR_HTTP_TIMEOUT", "60"))
TOKEN_SECRET = os.getenv("TOKEN_SECRET", "change-me")


def get_llm_url() -> str:
    """
    Determine which LLM endpoint to call based on environment variables.
    Always use the remote LM Studio server for deployment consistency.
    """
    return os.getenv("LLM_API_URL", "http://100.111.223.74:1234/v1/chat/completions")


__all__ = [
    "ASR_API_URL",
    "KOKORO_API_URL",
    "USE_LOCAL_LLM",
    "OPENROUTER_API_KEY",
    "DATABASE_URL",
    "VALIDATION_BUCKET",
    "ORCH_ENV",
    "LLM_MODE",
    "LM_LOCAL_URL",
    "LLM_OLLAMA_URL",
    "HTTP_TIMEOUT",
    "TOKEN_SECRET",
    "ORCHESTRATOR_AUDIO_DIR",
    "get_llm_url",
]
