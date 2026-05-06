"""Introspection utilities for the adaptive agent."""

from __future__ import annotations

from collections import Counter, deque
from statistics import mean
from typing import Any, Deque, Dict, List


class IntrospectiveState:
    """Tracks the internal history and meta-context for the agent.

    The state keeps a compact rolling memory rather than pretending to be an
    autonomous consciousness. It captures observable processing signals so the
    rest of the framework can explain what it did and why.
    """

    HISTORY_WINDOW = 5
    CONTEXT_TYPES = ("text", "sequence", "mapping", "numeric", "other")

    def __init__(self) -> None:
        self.history: List[Any] = []
        self.recent_contexts: Deque[Any] = deque(maxlen=self.HISTORY_WINDOW)
        self.meta_context: Dict[str, Any] = {}
        self.emotional_valence: float = 0.0
        self.valence_trace: Deque[float] = deque(maxlen=self.HISTORY_WINDOW)
        self.context_stats: Dict[str, int] = {name: 0 for name in self.CONTEXT_TYPES}
        self.adaptation_log: Deque[str] = deque(maxlen=self.HISTORY_WINDOW)
        self.signal_trace: Deque[List[str]] = deque(maxlen=self.HISTORY_WINDOW)
        self.transition_counts: Dict[str, int] = {}

    def observe(self, context: Any) -> None:
        """Store the incoming context and update summary information."""

        previous_descriptor = self.meta_context.get("last_descriptor")
        descriptor = self._describe_context(context)
        self.history.append(context)
        self.recent_contexts.append(context)
        self.context_stats[descriptor] = self.context_stats.get(descriptor, 0) + 1

        if previous_descriptor:
            transition = f"{previous_descriptor}->{descriptor}"
            self.transition_counts[transition] = (
                self.transition_counts.get(transition, 0) + 1
            )

        self.meta_context.update(
            {
                "last": context,
                "last_descriptor": descriptor,
                "last_size": self._estimate_size(context),
                "novelty_score": self._calculate_novelty(descriptor),
            }
        )

    def update_valence(self, delta: float) -> None:
        """Adjust the emotional valence and track the running average."""

        self.emotional_valence += delta
        self.valence_trace.append(self.emotional_valence)

    def record_adaptation(self, summary: str) -> None:
        """Add a short description of the latest adaptation."""

        self.adaptation_log.append(summary)

    def record_signal_bundle(self, signals: List[str]) -> None:
        """Remember the latest adaptation signals for reporting."""

        self.signal_trace.append(list(signals))

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
            "dominant_context_type": self._dominant_context_type(),
            "novelty_score": round(self.meta_context.get("novelty_score", 0.0), 4),
            "cognitive_load": round(self._cognitive_load(), 4),
            "recent_adaptations": list(self.adaptation_log),
            "recent_signals": [
                signal for bundle in self.signal_trace for signal in bundle
            ][-10:],
            "transition_counts": dict(self.transition_counts),
        }

    def summarize_recent_contexts(self) -> List[str]:
        """Return lightweight human-readable summaries for reflection."""

        summaries = []
        for ctx in self.recent_contexts:
            descriptor = self._describe_context(ctx)
            size = self._estimate_size(ctx)
            summaries.append(f"{descriptor} (size={size})")
        return summaries

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the current state to a dictionary."""

        return {
            "history": self.history,
            "recent_contexts": list(self.recent_contexts),
            "meta_context": self.meta_context,
            "emotional_valence": self.emotional_valence,
            "valence_trace": list(self.valence_trace),
            "context_stats": self.context_stats,
            "adaptation_log": list(self.adaptation_log),
            "signal_trace": list(self.signal_trace),
            "transition_counts": self.transition_counts,
        }

    def load_from_dict(self, data: Dict[str, Any]) -> None:
        """Restore the state from a dictionary."""

        self.history = data.get("history", [])
        self.recent_contexts = deque(
            data.get("recent_contexts", []), maxlen=self.HISTORY_WINDOW
        )
        self.meta_context = data.get("meta_context", {})
        self.emotional_valence = data.get("emotional_valence", 0.0)
        self.valence_trace = deque(
            data.get("valence_trace", []), maxlen=self.HISTORY_WINDOW
        )
        default_stats = {name: 0 for name in self.CONTEXT_TYPES}
        default_stats.update(data.get("context_stats", {}))
        self.context_stats = default_stats
        self.adaptation_log = deque(
            data.get("adaptation_log", []), maxlen=self.HISTORY_WINDOW
        )
        self.signal_trace = deque(
            data.get("signal_trace", []), maxlen=self.HISTORY_WINDOW
        )
        self.transition_counts = data.get("transition_counts", {})

    def _describe_context(self, context: Any) -> str:
        if isinstance(context, str):
            return "text"
        if isinstance(context, (list, tuple, set)):
            return "sequence"
        if isinstance(context, dict):
            return "mapping"
        if isinstance(context, (int, float)) and not isinstance(context, bool):
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

    def _calculate_novelty(self, descriptor: str) -> float:
        total = max(len(self.history), 1)
        descriptor_count = self.context_stats.get(descriptor, 0)
        return 1.0 - (descriptor_count / total)

    def _cognitive_load(self) -> float:
        if not self.recent_contexts:
            return 0.0
        recent_sizes = [self._estimate_size(ctx) for ctx in self.recent_contexts]
        diversity = len({self._describe_context(ctx) for ctx in self.recent_contexts})
        return min(1.0, (mean(recent_sizes) / 100.0) + (diversity / 10.0))

    def _dominant_context_type(self) -> str | None:
        populated = {key: value for key, value in self.context_stats.items() if value}
        if not populated:
            return None
        return Counter(populated).most_common(1)[0][0]
