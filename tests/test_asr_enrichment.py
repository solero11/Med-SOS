from types import SimpleNamespace

from src.utils.asr_enrichment import ASREnrichment, EnrichedSegment


class DummyWord:
    def __init__(self, start, end, word, probability):
        self.start = start
        self.end = end
        self.word = word
        self.probability = probability


class DummySegment:
    def __init__(self):
        self.start = 1.0
        self.end = 2.5
        self.text = "sat dropping ninety two"
        self.avg_logprob = -0.1
        self.compression_ratio = 1.1
        self.no_speech_prob = 0.2
        self.temperature = 0.0
        self.language = "en"
        self.words = [
            DummyWord(1.0, 1.3, "sat", 0.9),
            DummyWord(1.3, 1.8, "dropping", 0.8),
        ]


class DummyModel:
    def transcribe(self, path, **kwargs):
        return [DummySegment()], SimpleNamespace(language="en")


def test_transcribe_returns_enriched_segments(tmp_path):
    audio_path = tmp_path / "dummy.wav"
    audio_path.write_bytes(b"fake-audio")
    enricher = ASREnrichment(model=DummyModel())

    segments = enricher.transcribe(audio_path)

    assert len(segments) == 1
    seg = segments[0]
    assert isinstance(seg, EnrichedSegment)
    assert seg.t_start == 1.0
    assert 0.0 <= seg.noise_level <= 1.0
    assert abs(seg.confidence - 0.85) < 1e-6  # average of 0.9 and 0.8
    assert seg.metadata["words"][0]["text"] == "sat"


def test_to_scene_events_copies_metadata():
    seg = EnrichedSegment(
        t_start=0.0,
        t_end=1.0,
        text="example",
        confidence=0.9,
        noise_level=0.7,
        metadata={"avg_logprob": -0.2},
    )
    events = ASREnrichment.to_scene_events([seg])
    assert events[0].raw["noise_level"] == 0.7
    assert events[0].raw["avg_logprob"] == -0.2
