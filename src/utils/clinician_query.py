"""
Clinician query assistant for Socratic follow-up prompts.

This module inspects the current SBAR snapshot, recent event text, and any
loaded emergency protocols to decide which clarifying question the LLM should
ask the clinician. The goal is to prevent tunnel vision by requesting concrete
updates on vitals, interventions, or diagnostic gaps.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Sequence, Tuple

from src.schema.yaml_schema import EmergencyYAML
from src.utils.sbar_builder import SBAR


KEYWORD_QUESTION_MAP: Tuple[Tuple[Tuple[str, ...], str], ...] = (
    (("bp", "blood pressure", "pressure"), "Could you update the current blood pressure and any recent trends?"),
    (("sat", "spo2", "oxygen"), "What is the latest oxygen saturation and how has it been changing?"),
    (("etco2", "co2"), "Can you provide the most recent end-tidal CO2 value and trajectory?"),
    (("heart rate", "pulse", "tachy", "brady"), "What is the current heart rate and rhythm status?"),
    (("med", "drug", "dose", "phenylephrine", "epi", "vaso", "bolus"), "Which medications or interventions were given most recently and what was the response?"),
    (("procedure", "decompression", "tube", "needle", "line"), "What procedures have been performed so far and what were their outcomes?"),
)


def _normalize(text: Optional[str]) -> str:
    return (text or "").strip().lower()


@dataclass
class ClinicianQueryAssistant:
    """Generates follow-up questions to solicit missing clinical detail."""

    max_questions: int = 1
    default_question: str = "What additional clinical data would help clarify the situation?"
    _recent_questions: List[str] = field(default_factory=list)

    def reset(self) -> None:
        """Clear memory of previously asked questions."""
        self._recent_questions.clear()

    def _question_about_missing_fields(self, sbar: SBAR) -> List[str]:
        missing = sbar.missing_fields()
        prompts = []
        field_map = {
            "situation": "Can you summarize the current situation or most pressing concern?",
            "background": "What noteworthy background or comorbidities should we keep in mind?",
            "assessment": "What is your leading assessment or differential at this moment?",
            "recommendation": "What actions or next steps are being considered right now?",
        }
        for field in missing:
            prompt = field_map.get(field)
            if prompt:
                prompts.append(prompt)
        return prompts

    def _question_from_keywords(self, event_text: str) -> List[str]:
        lowered = _normalize(event_text)
        prompts = []
        for keywords, question in KEYWORD_QUESTION_MAP:
            if any(keyword in lowered for keyword in keywords):
                prompts.append(question)
        return prompts

    def _question_from_protocols(self, protocols: Sequence[EmergencyYAML]) -> List[str]:
        prompts: List[str] = []
        for doc in protocols:
            if doc.cognitive_prompts:
                focus = doc.cognitive_prompts[0]
                prompts.append(f"{focus.rstrip('?')}?")  # ensure interrogative
        return prompts

    def _dedupe(self, questions: Iterable[str]) -> List[str]:
        seen = set()
        output = []
        for question in questions:
            normalized = question.strip()
            if not normalized:
                continue
            if not normalized.endswith("?"):
                normalized = normalized.rstrip(".")
                normalized = f"{normalized}?"
            if normalized.lower() in seen:
                continue
            if normalized in self._recent_questions:
                continue
            seen.add(normalized.lower())
            output.append(normalized)
        return output

    def generate(
        self,
        *,
        sbar: SBAR,
        event_text: str,
        protocols: Sequence[EmergencyYAML] | None = None,
        additional_context: Optional[str] = None,
    ) -> List[str]:
        """
        Produce up to `max_questions` clinician-facing prompts.

        Parameters
        ----------
        sbar: SBAR
            Current SBAR snapshot.
        event_text: str
            Most recent observation or utterance.
        protocols: Sequence[EmergencyYAML] | None
            Loaded emergency protocols relevant to the scene.
        additional_context: Optional[str]
            Optional supplementary text (unused for heuristics but kept for future LLM hooks).
        """
        candidates: List[str] = []
        candidates.extend(self._question_from_keywords(event_text))
        candidates.extend(self._question_about_missing_fields(sbar))
        if protocols:
            candidates.extend(self._question_from_protocols(protocols))

        deduped = self._dedupe(candidates)
        if not deduped:
            deduped = [self.default_question]
        selected = deduped[: self.max_questions]
        self._recent_questions.extend(selected)
        return selected


__all__ = ["ClinicianQueryAssistant"]
