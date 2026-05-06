"""Reflection module for the adaptive agent."""

from __future__ import annotations

from typing import Optional

if __package__:
    from .adaptation import AdaptationResult
else:
    from adaptation import AdaptationResult


class ReflectiveProcessor:
    """Generate compact narrative summaries from state and adaptation output."""

    def __init__(self, state):
        self.state = state

    def reflect(self, adaptation: Optional[AdaptationResult]) -> str:
        if not self.state.history:
            return "No context to reflect on."

        report = self.state.report()
        summaries = ", ".join(self.state.summarize_recent_contexts())
        valence = self.state.emotional_valence
        trend = report["valence_trend"]
        dominant = report["dominant_context_type"] or "n/a"
        novelty = report["recent_context_novelty"]
        adaptation_summary = adaptation.summary if adaptation else "No new adaptation"
        confidence = adaptation.confidence if adaptation else 0.0
        return (
            "Reflection: "
            f"observed {len(self.state.history)} contexts; "
            f"recent types: {summaries or 'n/a'}; "
            f"dominant type: {dominant}; "
            f"latest adaptation: {adaptation_summary}; "
            f"confidence={confidence:.2f}; "
            f"novelty={novelty:.2f}; "
            f"valence={valence:.2f}, trend={trend:.2f}"
        )
