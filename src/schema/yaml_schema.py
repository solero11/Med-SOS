"""
Canonical schema definition for emergency YAML "books".

This module exposes a Pydantic model that enforces the hybrid, question-first
structure we use throughout the ingestion and retrieval pipeline.
"""
from __future__ import annotations

from typing import List, Optional

try:
    # Prefer the Pydantic v1 compatibility layer when running under Pydantic v2+
    from pydantic.v1 import BaseModel, Field, conlist, constr
    from pydantic import field_validator
except ImportError:  # Genuine Pydantic v1 environment
    from pydantic import BaseModel, Field, conlist, constr
    from pydantic import validator as _legacy_validator

    def field_validator(*fields, **kwargs):
        """Shim `field_validator` API onto the legacy `validator` decorator."""
        mode = kwargs.pop("mode", None)
        if mode is not None:
            kwargs["pre"] = mode == "before"
        return _legacy_validator(*fields, **kwargs)


def _compat_constr(*args, **kwargs):
    """
    Allow the schema to work across Pydantic v1 and v2 where the keyword
    arguments changed from `regex` to `pattern`.
    """
    try:
        return constr(*args, **kwargs)
    except TypeError:
        if "regex" in kwargs:
            kwargs = dict(kwargs)
            kwargs["pattern"] = kwargs.pop("regex")
            return constr(*args, **kwargs)
        raise

def _compat_conlist(item_type, *, min_items: int | None = None, max_items: int | None = None):
    """
    Bridge the signature difference for conlist between Pydantic v1 and v2.
    """
    kwargs = {}
    if min_items is not None:
        kwargs["min_items"] = min_items
    if max_items is not None:
        kwargs["max_items"] = max_items
    try:
        return conlist(item_type, **kwargs)
    except TypeError:
        adjusted = {}
        if min_items is not None:
            adjusted["min_length"] = min_items
        if max_items is not None:
            adjusted["max_length"] = max_items
        return conlist(item_type, **adjusted)


# Reusable constrained string types
ShortStr = _compat_constr(strip_whitespace=True, min_length=1, max_length=160)
ClauseStr = _compat_constr(strip_whitespace=True, min_length=1, max_length=180)
SummaryStr = _compat_constr(strip_whitespace=True, min_length=1, max_length=480)
SlugStr = _compat_constr(regex=r"^[a-z0-9_]+$", min_length=3, max_length=64)
IsoDateStr = _compat_constr(regex=r"^\d{4}-\d{2}-\d{2}$")


class Meta(BaseModel):
    """Metadata capturing relationships without requiring nested folders."""

    id: SlugStr = Field(..., description="Unique slug, e.g. 'hypotension_intraop'")
    title: ShortStr = Field(..., description="Human-readable title")
    parent: Optional[SlugStr] = Field(
        None, description="Conceptual family id from registry.yaml"
    )
    aliases: _compat_conlist(ShortStr, min_items=0, max_items=16) = Field(default_factory=list)
    keywords: _compat_conlist(ShortStr, min_items=0, max_items=24) = Field(default_factory=list)
    related_topics: _compat_conlist(SlugStr, min_items=0, max_items=16) = Field(
        default_factory=list
    )
    priority: float = Field(
        0.5, ge=0.0, le=1.0, description="Retriever weighting hint (0.0-1.0)"
    )
    version: Optional[IsoDateStr] = Field(
        None, description="YYYY-MM-DD version stamp (set when curated)"
    )


class UpdateConflicts(BaseModel):
    """Tracks merge conflicts when multiple sources feed the YAML maker."""

    added_from_sources: _compat_conlist(ShortStr, min_items=0, max_items=64) = Field(
        default_factory=list
    )
    removed_from_sources: _compat_conlist(ShortStr, min_items=0, max_items=64) = Field(
        default_factory=list
    )
    unresolved_conflicts: _compat_conlist(ShortStr, min_items=0, max_items=64) = Field(
        default_factory=list
    )


class Provenance(BaseModel):
    """Minimal provenance for audit trails."""

    last_sources: _compat_conlist(ShortStr, min_items=0, max_items=64) = Field(
        default_factory=list, description="Opaque source identifiers or filenames"
    )
    merged_on: Optional[IsoDateStr] = Field(
        None, description="Date the YAML was last consolidated"
    )


class EmergencyYAML(BaseModel):
    """Primary schema enforcing the hybrid emergency-book structure."""

    meta: Meta
    summary: SummaryStr = Field(
        ..., description="Distilled overview (no citations, no directives)"
    )

    signals: _compat_conlist(ClauseStr, min_items=1, max_items=12)
    red_flags: _compat_conlist(ClauseStr, min_items=0, max_items=12) = Field(
        default_factory=list
    )
    primary_differential: _compat_conlist(ShortStr, min_items=1, max_items=8)
    first_checks: _compat_conlist(ClauseStr, min_items=1, max_items=12)
    cognitive_prompts: _compat_conlist(ClauseStr, min_items=1, max_items=12)
    contraindications_notes: _compat_conlist(ClauseStr, min_items=0, max_items=12) = Field(
        default_factory=list
    )

    subtopics: Optional[List[dict]] = Field(
        default=None,
        description="Optional micro-variants; each a small dict with name/signals/notes",
    )

    update_conflicts: UpdateConflicts = Field(default_factory=UpdateConflicts)
    provenance: Provenance = Field(default_factory=Provenance)

    @staticmethod
    def _ensure_prompt(value: str) -> str:
        bad_starts = ("Give ", "Administer ", "Inject ", "Start ", "Stop ", "Bolus ")
        if any(value.startswith(prefix) for prefix in bad_starts):
            raise ValueError("Cognitive prompts must be interrogative, not imperative.")
        return value

    @field_validator("cognitive_prompts", mode="before")
    def _ensure_prompts_are_questions(cls, value):
        if value is None:
            return value
        if isinstance(value, list):
            return [cls._ensure_prompt(item) for item in value]
        return cls._ensure_prompt(value)

    @field_validator("summary", mode="before")
    def _prevent_citations_in_summary(cls, value: str):
        if value is None:
            return value
        banned_tokens = ("http://", "https://", "doi:", "et al.", "Figure", "Table")
        if any(token in value for token in banned_tokens):
            raise ValueError("Summary must be distilled and source-agnostic.")
        return value


__all__ = ["EmergencyYAML", "Meta", "UpdateConflicts", "Provenance"]
