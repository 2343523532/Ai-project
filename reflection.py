"""Reflection module for the adaptive agent."""

from __future__ import annotations

from typing import Optional

if __package__:
    from .adaptation import AdaptationResult
else:
    from adaptation import AdaptationResult


class ReflectiveProcessor:
    """Creates a compact explanation of the agent's latest processing cycle."""

    def __init__(self, state):
        self.state = state

    def reflect(self, adaptation: Optional[AdaptationResult]) -> str:
        if not self.state.history:
            return "No context to reflect on."

        report = self.state.report()
        summaries = ", ".join(self.state.summarize_recent_contexts())
        valence = self.state.emotional_valence
        trend = report["valence_trend"]
        adaptation_summary = adaptation.summary if adaptation else "No new adaptation"
        strategy = adaptation.strategy if adaptation else "none"
        confidence = adaptation.confidence if adaptation else 0.0
        signals = (
            ", ".join(adaptation.signals)
            if adaptation and adaptation.signals
            else "none"
        )
        next_focus = self._recommend_next_focus(report, adaptation)
        return (
            "Reflection: "
            f"observed {len(self.state.history)} contexts; "
            f"recent types: {summaries or 'n/a'}; "
            f"latest adaptation: {adaptation_summary}; "
            f"strategy={strategy}; confidence={confidence:.2f}; "
            f"signals={signals}; "
            f"novelty={report['novelty_score']:.2f}; "
            f"cognitive_load={report['cognitive_load']:.2f}; "
            f"valence={valence:.2f}, trend={trend:.2f}; "
            f"next_focus={next_focus}"
        )

    def _recommend_next_focus(
        self, report: dict, adaptation: Optional[AdaptationResult]
    ) -> str:
        """Suggest a deterministic next focus from observable state metrics."""

        if not adaptation:
            return "collect_more_context"
        if report["cognitive_load"] >= 0.75:
            return "summarize_or_chunk_inputs"
        if report["novelty_score"] >= 0.6:
            return "compare_against_prior_contexts"
        if adaptation.confidence < 0.5:
            return "request_more_structured_input"
        if "repetition_detected" in adaptation.signals:
            return "compress_repeated_terms"
        return "continue_monitoring_patterns"
