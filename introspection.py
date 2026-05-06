"""Introspection utilities for the adaptive agent."""

from __future__ import annotations

from collections import deque
from copy import deepcopy
from statistics import mean
from typing import Any, Deque, Dict, List


class IntrospectiveState:
    """Tracks history, metrics, and rolling diagnostics for the agent."""

    HISTORY_WINDOW = 5
    DEFAULT_CONTEXT_STATS = {
        "text": 0,
        "sequence": 0,
        "mapping": 0,
        "numeric": 0,
        "boolean": 0,
        "other": 0,
    }

    def __init__(self) -> None:
        self.history: List[Any] = []
        self.recent_contexts: Deque[Any] = deque(maxlen=self.HISTORY_WINDOW)
        self.meta_context: Dict[str, Any] = {}
        self.emotional_valence: float = 0.0
        self.valence_trace: Deque[float] = deque(maxlen=self.HISTORY_WINDOW)
        self.context_stats: Dict[str, int] = dict(self.DEFAULT_CONTEXT_STATS)
        self.adaptation_log: Deque[str] = deque(maxlen=self.HISTORY_WINDOW)
        self.observation_log: Deque[Dict[str, Any]] = deque(maxlen=self.HISTORY_WINDOW)

    def observe(self, context: Any) -> None:
        """Store the incoming context and update summary information."""

        descriptor = self._describe_context(context)
        size = self._estimate_size(context)
        novelty = self.novelty_score(context)

        self.history.append(context)
        self.recent_contexts.append(context)
        self.context_stats[descriptor] = self.context_stats.get(descriptor, 0) + 1
        observation = {
            "index": len(self.history),
            "descriptor": descriptor,
            "size": size,
            "novelty_score": novelty,
        }
        self.observation_log.append(observation)

        self.meta_context.update(
            {
                "last": context,
                "last_descriptor": descriptor,
                "last_size": size,
                "last_novelty_score": novelty,
                "last_observation": observation,
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
            "recent_context_novelty": round(self.meta_context.get("last_novelty_score", 0.0), 4),
            "emotional_valence": round(self.emotional_valence, 4),
            "valence_trend": round(rolling_average, 4),
            "context_stats": dict(self.context_stats),
            "dominant_context_type": self.dominant_context_type(),
            "recent_adaptations": list(self.adaptation_log),
            "observation_log": list(self.observation_log),
        }

    def summarize_recent_contexts(self) -> List[str]:
        """Return lightweight human-readable summaries for reflection."""

        summaries = []
        for ctx in self.recent_contexts:
            descriptor = self._describe_context(ctx)
            size = self._estimate_size(ctx)
            summaries.append(f"{descriptor} (size={size})")
        return summaries

    def novelty_score(self, context: Any) -> float:
        """Estimate whether the context differs from the current rolling window."""

        if not self.recent_contexts:
            return 1.0
        descriptor = self._describe_context(context)
        descriptor_matches = sum(
            1 for recent in self.recent_contexts if self._describe_context(recent) == descriptor
        )
        repetition_penalty = descriptor_matches / len(self.recent_contexts)
        return round(max(0.0, 1.0 - repetition_penalty), 4)

    def dominant_context_type(self) -> str | None:
        """Return the most frequently observed context descriptor."""

        non_zero = {key: value for key, value in self.context_stats.items() if value > 0}
        if not non_zero:
            return None
        return max(non_zero, key=non_zero.get)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the current state to a dictionary."""

        return {
            "history": deepcopy(self.history),
            "recent_contexts": list(self.recent_contexts),
            "meta_context": deepcopy(self.meta_context),
            "emotional_valence": self.emotional_valence,
            "valence_trace": list(self.valence_trace),
            "context_stats": dict(self.context_stats),
            "adaptation_log": list(self.adaptation_log),
            "observation_log": list(self.observation_log),
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
        self.context_stats = dict(self.DEFAULT_CONTEXT_STATS)
        self.context_stats.update(data.get("context_stats", {}))
        self.adaptation_log = deque(
            data.get("adaptation_log", []), maxlen=self.HISTORY_WINDOW
        )
        self.observation_log = deque(
            data.get("observation_log", []), maxlen=self.HISTORY_WINDOW
        )

    def _describe_context(self, context: Any) -> str:
        if isinstance(context, str):
            return "text"
        if isinstance(context, bool):
            return "boolean"
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
