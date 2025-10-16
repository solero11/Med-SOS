"""
Audio integration package for microphone capture and speech services.

This module exposes thin clients for the external ASR/TTS microservices along
with orchestration helpers used by the SOS UI.
"""

from .asr_client import ASRClient, ASRConfig, ASRTranscript
from .tts_client import TTSClient, TTSConfig, TTSAudio
from .pipeline import ConversationPipeline, PipelineResult
from .microphone import MicrophoneRecorder, MicrophoneUnavailableError, VoiceActivityEvent

__all__ = [
    "ASRClient",
    "ASRConfig",
    "ASRTranscript",
    "TTSClient",
    "TTSConfig",
    "TTSAudio",
    "ConversationPipeline",
    "PipelineResult",
    "MicrophoneRecorder",
    "MicrophoneUnavailableError",
    "VoiceActivityEvent",
]
