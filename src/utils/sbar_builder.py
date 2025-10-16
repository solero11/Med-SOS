"""
SBAR Builder Utility

This module provides functions to build and manage SBAR (Situation, Background, Assessment, Recommendation) data objects from conversational input.
"""

from typing import Optional, Dict

class SBAR:
    FIELDS = ("situation", "background", "assessment", "recommendation")

    def __init__(self, situation: Optional[str] = None, background: Optional[str] = None,
                 assessment: Optional[str] = None, recommendation: Optional[str] = None):
        self.situation = situation
        self.background = background
        self.assessment = assessment
        self.recommendation = recommendation

    def to_dict(self) -> Dict[str, Optional[str]]:
        return {
            "situation": self.situation,
            "background": self.background,
            "assessment": self.assessment,
            "recommendation": self.recommendation
        }

    def _is_filled(self, value: Optional[str]) -> bool:
        if value is None:
            return False
        if isinstance(value, str):
            return value.strip() != ""
        return bool(value)

    def is_complete(self) -> bool:
        return all(self._is_filled(getattr(self, field)) for field in self.FIELDS)

    def missing_fields(self) -> list:
        return [
            field for field in self.FIELDS
            if not self._is_filled(getattr(self, field))
        ]

    def __repr__(self):
        return f"SBAR(situation={self.situation!r}, background={self.background!r}, assessment={self.assessment!r}, recommendation={self.recommendation!r})"
