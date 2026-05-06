"""Adaptive reasoning loop for the agent."""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional

import numpy as np


@dataclass
class AdaptationResult:
    """Structured response produced by the adaptive loop."""

    summary: str
    details: Dict[str, Any]
    strategy: str = "general"
    confidence: float = 0.5
    signals: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Return a serializable representation of the adaptation result."""

        return {
            "summary": self.summary,
            "strategy": self.strategy,
            "confidence": round(self.confidence, 4),
            "signals": list(self.signals),
            "details": self.details,
        }


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
        self.state.record_signal_bundle(result.signals)
        return result

    def _adapt_context(self, context: Any) -> AdaptationResult:
        if isinstance(context, str):
            return self._adapt_text(context)

        if isinstance(context, (list, tuple, set, np.ndarray)):
            return self._adapt_sequence(context)

        if isinstance(context, dict):
            return self._adapt_mapping(context)

        if isinstance(context, (int, float)) and not isinstance(context, bool):
            return self._adapt_numeric(context)

        summary = "Processed miscellaneous context"
        details = {
            "representation": repr(context),
            "type_name": type(context).__name__,
            "valence_delta": 0.005,
        }
        return AdaptationResult(
            summary=summary,
            details=details,
            strategy="fallback-representation",
            confidence=0.35,
            signals=["unknown_type"],
        )

    def _adapt_text(self, context: str) -> AdaptationResult:
        tokens = re.findall(r"\b[\w'-]+\b", context.lower())
        unique_tokens = len(set(tokens))
        token_count = len(tokens)
        lexical_diversity = unique_tokens / token_count if token_count else 0.0
        repeated_terms = [
            term for term, count in Counter(tokens).most_common(5) if count > 1
        ]
        sentence_count = len(
            [part for part in re.split(r"[.!?]+", context) if part.strip()]
        )
        avg_token_length = (
            sum(len(token) for token in tokens) / token_count if token_count else 0.0
        )
        signals = ["empty_text"] if not context.strip() else ["textual_signal"]
        if lexical_diversity >= 0.8 and token_count >= 4:
            signals.append("high_lexical_diversity")
        if repeated_terms:
            signals.append("repetition_detected")

        details = {
            "transformation": "reverse_and_profile",
            "token_count": token_count,
            "unique_tokens": unique_tokens,
            "lexical_diversity": round(lexical_diversity, 4),
            "sentence_count": sentence_count,
            "average_token_length": round(avg_token_length, 2),
            "repeated_terms": repeated_terms,
            "reversed": context[::-1],
            "valence_delta": 0.02 if unique_tokens else 0.01,
        }
        return AdaptationResult(
            summary="Processed textual context with lexical profiling",
            details=details,
            strategy="text-lexical-profiler",
            confidence=self._confidence_from_density(token_count, unique_tokens),
            signals=signals,
        )

    def _adapt_sequence(self, context: Iterable[Any]) -> AdaptationResult:
        sequence = list(context)
        numeric = self._is_numeric_sequence(sequence)
        numeric_stats: Dict[str, Any] = {
            "mean": None,
            "median": None,
            "minimum": None,
            "maximum": None,
            "std_dev": None,
        }
        if numeric and sequence:
            values = [float(item) for item in sequence]
            numeric_stats = {
                "mean": float(np.mean(values)),
                "median": float(np.median(values)),
                "minimum": float(np.min(values)),
                "maximum": float(np.max(values)),
                "std_dev": float(np.std(values)),
            }

        type_mix = dict(Counter(type(item).__name__ for item in sequence))
        details = {
            "transformation": "reverse_and_measure",
            "length": len(sequence),
            "is_numeric": numeric,
            "type_mix": type_mix,
            "reversed": list(reversed(sequence)),
            "valence_delta": 0.015 if sequence else 0.004,
            **numeric_stats,
        }
        signals = ["sequence_signal"]
        if numeric:
            signals.append("numeric_sequence")
        if len(type_mix) > 1:
            signals.append("heterogeneous_sequence")

        return AdaptationResult(
            summary="Processed sequence context with distribution metrics",
            details=details,
            strategy="sequence-distribution-analyzer",
            confidence=0.72 if sequence else 0.42,
            signals=signals,
        )

    def _adapt_mapping(self, context: Dict[Any, Any]) -> AdaptationResult:
        value_types = dict(Counter(type(value).__name__ for value in context.values()))
        nested_keys = [
            key
            for key, value in context.items()
            if isinstance(value, (dict, list, tuple, set))
        ]
        numeric_values = [
            value
            for value in context.values()
            if isinstance(value, (int, float)) and not isinstance(value, bool)
        ]
        details = {
            "keys": list(context.keys()),
            "values": list(context.values()),
            "key_count": len(context),
            "value_types": value_types,
            "nested_keys": nested_keys,
            "numeric_value_count": len(numeric_values),
            "numeric_value_mean": (
                float(np.mean(numeric_values)) if numeric_values else None
            ),
            "valence_delta": 0.012 if context else 0.004,
        }
        signals = ["mapping_signal"]
        if nested_keys:
            signals.append("nested_structure")
        if numeric_values:
            signals.append("numeric_fields")

        return AdaptationResult(
            summary="Processed mapping context with schema profiling",
            details=details,
            strategy="mapping-schema-profiler",
            confidence=0.76 if context else 0.45,
            signals=signals,
        )

    def _adapt_numeric(self, context: float) -> AdaptationResult:
        magnitude = abs(float(context))
        details = {
            "value": context,
            "normalized": self._normalize_numeric(float(context)),
            "magnitude": magnitude,
            "order_of_magnitude": math.floor(math.log10(magnitude)) if magnitude else 0,
            "polarity": (
                "positive" if context > 0 else "negative" if context < 0 else "zero"
            ),
            "valence_delta": 0.01,
        }
        return AdaptationResult(
            summary="Processed numeric context with magnitude analysis",
            details=details,
            strategy="numeric-signal-normalizer",
            confidence=0.8,
            signals=["numeric_signal", details["polarity"]],
        )

    @staticmethod
    def _is_numeric_sequence(sequence: Iterable[Any]) -> bool:
        return all(
            isinstance(item, (int, float)) and not isinstance(item, bool)
            for item in sequence
        )

    @staticmethod
    def _normalize_numeric(value: float) -> float:
        if value >= 0:
            z = math.exp(-value) if value < 709 else 0.0
            return 1 / (1 + z)
        z = math.exp(value) if value > -709 else 0.0
        return z / (1 + z)

    @staticmethod
    def _confidence_from_density(token_count: int, unique_tokens: int) -> float:
        if token_count == 0:
            return 0.4
        density = unique_tokens / token_count
        return min(0.95, 0.5 + (density * 0.4) + min(token_count, 20) / 200)
