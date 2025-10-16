"""
Conversation pipeline bridging ASR, LLM, and TTS services.

The pipeline is intentionally lightweight so interactive clients (e.g. the SOS
button UI) can orchestrate a single request at a time while reusing a shared
conversation history.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from src.llm.llm_client import LLMClient

from .asr_client import ASRClient, ASRTranscript
from .tts_client import TTSClient, TTSAudio


@dataclass(slots=True)
class PipelineResult:
    """Combined output for a single request/response turn."""

    transcript: ASRTranscript
    llm_response: str
    audio: Optional[TTSAudio]


@dataclass
class ConversationPipeline:
    """
    Glue object that:
      1. Sends microphone audio to ASR.
      2. Feeds the transcript to the LLM (with rolling history).
      3. Converts the LLM reply to speech via Kokoro.
    """

    asr: ASRClient
    llm: LLMClient
    tts: TTSClient
    history: List[Dict[str, str]] = field(default_factory=list)
    auto_tts: bool = True

    def reset(self) -> None:
        """Clear conversation history."""
        self.history.clear()

    def process_audio(
        self,
        audio_bytes: bytes,
        *,
        language: Optional[str] = None,
        generate_audio: Optional[bool] = None,
    ) -> PipelineResult:
        """Execute a full user→assistant turn."""
        transcript = self.asr.transcribe_bytes(audio_bytes, language=language)
        user_text = transcript.text.strip()

        if not user_text:
            # Nothing to say back – return empty reply without touching history.
            return PipelineResult(transcript=transcript, llm_response="", audio=None)

        # Update history and query the LLM.
        self.history.append({"role": "user", "content": user_text})
        assistant_reply = self.llm.ask(user_text, history=self.history[:-1])
        self.history.append({"role": "assistant", "content": assistant_reply})

        should_generate_audio = self.auto_tts if generate_audio is None else generate_audio
        tts_audio = self.tts.speak(assistant_reply) if should_generate_audio else None

        return PipelineResult(
            transcript=transcript,
            llm_response=assistant_reply,
            audio=tts_audio,
        )
