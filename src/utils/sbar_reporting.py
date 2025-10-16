"""
Shared SBAR reporting helpers.

Provides lightweight dataclasses and Markdown builders that can be reused by
CLI harnesses and tests without pulling in LM Studio dependencies.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence


@dataclass
class SBARSnapshot:
    """Immutable snapshot of an SBAR state captured at a scene timestamp."""

    index: int
    t_start: float
    event_text: str
    sbar: Dict[str, Optional[str]]


@dataclass
class QuestionEntry:
    """Represents a single LLM-generated cognitive prompt."""

    index: int
    t_start: float
    event_text: str
    question: str
    answer: Optional[str] = None


def format_sbar_line(sbar_map: Dict[str, Optional[str]]) -> str:
    return (
        f"Situation: {sbar_map.get('situation') or 'None'} | "
        f"Background: {sbar_map.get('background') or 'None'} | "
        f"Assessment: {sbar_map.get('assessment') or 'None'} | "
        f"Recommendation: {sbar_map.get('recommendation') or 'None'}"
    )


def build_markdown_body(initial_sbar: Dict[str, Optional[str]], snapshots: List[SBARSnapshot]) -> str:
    """
    Render the SBAR progression without critique or ancillary sections.
    """
    lines: List[str] = ["# SBAR Evolution Report", ""]
    lines.append("## Initial SBAR")
    lines.append("")
    if any(initial_sbar.values()):
        for field, value in initial_sbar.items():
            lines.append(f"- **{field.capitalize()}**: {value or 'None'}")
    else:
        lines.append("All fields empty at start.")
    lines.append("")
    lines.append("## Significant Updates")
    lines.append("")
    if not snapshots:
        lines.append("No significant changes were detected during playback.")
    else:
        for snap in snapshots:
            lines.append(f"### Update {snap.index} (t={snap.t_start:.1f}s)")
            lines.append(f"- **Observation**: {snap.event_text}")
            for field, value in snap.sbar.items():
                display = value or "None"
                lines.append(f"  - {field.capitalize()}: {display}")
            lines.append("")
    return "\n".join(lines).strip() + "\n"


def render_markdown(
    initial_sbar: Dict[str, Optional[str]],
    snapshots: List[SBARSnapshot],
    critique: str,
) -> str:
    """
    Build the full report including the critique section.
    """
    body = build_markdown_body(initial_sbar, snapshots)
    lines = [body.rstrip(), "", "## LLM Critique", ""]
    lines.append(critique.strip() or "_No critique provided._")
    lines.append("")
    return "\n".join(lines)


def build_questions_markdown(entries: Sequence[QuestionEntry]) -> str:
    """
    Format Socratic question prompts for clinician review.
    """
    lines: List[str] = ["# Clinician Reflection Prompts", ""]
    if not entries:
        lines.append("_No questions generated._")
        lines.append("")
        return "\n".join(lines)
    for entry in entries:
        lines.append(f"## Update {entry.index} (t={entry.t_start:.1f}s)")
        lines.append(f"- Observation: {entry.event_text}")
        lines.append(f"- Question: {entry.question}")
        if entry.answer:
            lines.append(f"- Answer: {entry.answer}")
        lines.append("")
    return "\n".join(lines)


__all__ = [
    "SBARSnapshot",
    "QuestionEntry",
    "build_markdown_body",
    "render_markdown",
    "build_questions_markdown",
    "format_sbar_line",
]
