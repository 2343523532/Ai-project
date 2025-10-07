"""Adaptive reasoning loop for the agent."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional

import numpy as np


@dataclass
class AdaptationResult:
    """Structured response produced by the adaptive loop."""

    summary: str
    details: Dict[str, Any]


class AdaptiveLoop:
    """Compute a best-effort adaptation based on the latest context."""

    def __init__(self, state) -> None:
        self.state = state

    def run(self) -> Optional[AdaptationResult]:
        if not self.state.history:
            return None

        last = self.state.history[-1]
        result = self._adapt_context(last)
        self.state.update_valence(result.details.get("valence_delta", 0.0))
        self.state.record_adaptation(result.summary)
        return result

    def _adapt_context(self, context: Any) -> AdaptationResult:
        if isinstance(context, str):
            reversed_text = context[::-1]
            tokens = context.split()
            unique_tokens = len(set(tokens)) if tokens else 0
            summary = "Processed textual context"
            details = {
                "transformation": "reverse",
                "token_count": len(tokens),
                "unique_tokens": unique_tokens,
                "reversed": reversed_text,
                "valence_delta": 0.02 if unique_tokens else 0.01,
            }
            return AdaptationResult(summary=summary, details=details)

        if isinstance(context, (list, tuple, set, np.ndarray)):
            sequence = list(context)
            reversed_sequence = list(reversed(sequence))
            mean_value = float(np.mean(sequence)) if self._is_numeric_sequence(sequence) else None
            summary = "Processed sequence context"
            details = {
                "transformation": "reverse",
                "length": len(sequence),
                "mean": mean_value,
                "reversed": reversed_sequence,
                "valence_delta": 0.015,
            }
            return AdaptationResult(summary=summary, details=details)

        if isinstance(context, dict):
            summary = "Processed mapping context"
            details = {
                "keys": list(context.keys()),
                "values": list(context.values()),
                "valence_delta": 0.012,
            }
            return AdaptationResult(summary=summary, details=details)

        if isinstance(context, (int, float)):
            summary = "Processed numeric context"
            details = {
                "value": context,
                "normalized": self._normalize_numeric(context),
                "valence_delta": 0.01,
            }
            return AdaptationResult(summary=summary, details=details)

        summary = "Processed miscellaneous context"
        details = {"representation": repr(context), "valence_delta": 0.005}
        return AdaptationResult(summary=summary, details=details)

    @staticmethod
    def _is_numeric_sequence(sequence: Iterable[Any]) -> bool:
        return all(isinstance(item, (int, float)) for item in sequence)

    @staticmethod
    def _normalize_numeric(value: float) -> float:
        return 1 / (1 + np.exp(-value))
