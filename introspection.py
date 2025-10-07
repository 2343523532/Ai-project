"""Introspection utilities for the adaptive agent."""

from __future__ import annotations

from collections import deque
from statistics import mean
from typing import Any, Deque, Dict, List


class IntrospectiveState:
    """Tracks the internal history and meta-context for the agent.

    The original project stored only the latest context and a simple valence
    value.  To make the agent more informative we now maintain:

    - A rolling memory of recent contexts for lightweight analysis.
    - Type statistics for quick introspective reporting.
    - A history of valence updates so we can provide trend information.
    - A registry of the most recent adaptations for later reflection.
    """

    HISTORY_WINDOW = 5

    def __init__(self) -> None:
        self.history: List[Any] = []
        self.recent_contexts: Deque[Any] = deque(maxlen=self.HISTORY_WINDOW)
        self.meta_context: Dict[str, Any] = {}
        self.emotional_valence: float = 0.0
        self.valence_trace: Deque[float] = deque(maxlen=self.HISTORY_WINDOW)
        self.context_stats: Dict[str, int] = {
            "text": 0,
            "sequence": 0,
            "mapping": 0,
            "numeric": 0,
            "other": 0,
        }
        self.adaptation_log: Deque[str] = deque(maxlen=self.HISTORY_WINDOW)

    def observe(self, context: Any) -> None:
        """Store the incoming context and update summary information."""

        self.history.append(context)
        self.recent_contexts.append(context)
        descriptor = self._describe_context(context)
        self.context_stats[descriptor] += 1

        self.meta_context.update(
            {
                "last": context,
                "last_descriptor": descriptor,
                "last_size": self._estimate_size(context),
            }
        )

    def update_valence(self, delta: float) -> None:
        """Adjust the emotional valence and track the running average."""

        self.emotional_valence += delta
        self.valence_trace.append(self.emotional_valence)

    def record_adaptation(self, summary: str) -> None:
        """Add a short description of the latest adaptation."""

        self.adaptation_log.append(summary)

    def report(self) -> Dict[str, Any]:
        """Produce an introspection report consumed by downstream modules."""

        rolling_average = mean(self.valence_trace) if self.valence_trace else 0.0
        return {
            "history_length": len(self.history),
            "recent_context": self.meta_context.get("last"),
            "recent_context_descriptor": self.meta_context.get("last_descriptor"),
            "recent_context_size": self.meta_context.get("last_size"),
            "emotional_valence": round(self.emotional_valence, 4),
            "valence_trend": round(rolling_average, 4),
            "context_stats": dict(self.context_stats),
            "recent_adaptations": list(self.adaptation_log),
        }

    def summarize_recent_contexts(self) -> List[str]:
        """Return lightweight human-readable summaries for reflection."""

        summaries = []
        for ctx in self.recent_contexts:
            descriptor = self._describe_context(ctx)
            size = self._estimate_size(ctx)
            summaries.append(f"{descriptor} (size={size})")
        return summaries

    def _describe_context(self, context: Any) -> str:
        if isinstance(context, str):
            return "text"
        if isinstance(context, (list, tuple, set)):
            return "sequence"
        if isinstance(context, dict):
            return "mapping"
        if isinstance(context, (int, float)):
            return "numeric"
        return "other"

    def _estimate_size(self, context: Any) -> int:
        if isinstance(context, str):
            return len(context)
        if isinstance(context, (list, tuple, set)):
            return len(context)
        if isinstance(context, dict):
            return len(context.keys())
        return 1
