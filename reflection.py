"""Reflection module for the adaptive agent."""

from __future__ import annotations

from typing import Optional

if __package__:
    from .adaptation import AdaptationResult
else:
    from adaptation import AdaptationResult


class ReflectiveProcessor:
    def __init__(self, state):
        self.state = state

    def reflect(self, adaptation: Optional[AdaptationResult]) -> str:
        if not self.state.history:
            return "No context to reflect on."

        summaries = ", ".join(self.state.summarize_recent_contexts())
        valence = self.state.emotional_valence
        trend = self.state.report()["valence_trend"]
        adaptation_summary = adaptation.summary if adaptation else "No new adaptation"
        return (
            "Reflection: "
            f"observed {len(self.state.history)} contexts; "
            f"recent types: {summaries or 'n/a'}; "
            f"latest adaptation: {adaptation_summary}; "
            f"valence={valence:.2f}, trend={trend:.2f}"
        )
