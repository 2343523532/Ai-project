"""Adaptive reasoning loop for the agent.

The module intentionally models *adaptive behavior* rather than claiming real
sentience.  It extracts practical signals from each input context, estimates a
confidence score, and returns next-step recommendations that callers can act on.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import log2
from typing import Any, Dict, Iterable, List, Optional

import numpy as np


@dataclass
class AdaptationResult:
    """Structured response produced by the adaptive loop."""

    summary: str
    details: Dict[str, Any]
    confidence: float = 0.0
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-friendly representation of the adaptation result."""

        return {
            "summary": self.summary,
            "details": self.details,
            "confidence": round(self.confidence, 4),
            "recommendations": list(self.recommendations),
        }


class AdaptiveLoop:
    """Compute a best-effort adaptation based on the latest context."""

    POSITIVE_MARKERS = {
        "better",
        "clear",
        "excellent",
        "great",
        "improve",
        "stable",
        "success",
        "useful",
    }
    NEGATIVE_MARKERS = {
        "bad",
        "broken",
        "error",
        "fail",
        "risk",
        "unstable",
        "worse",
    }

    def __init__(self, state) -> None:
        self.state = state

    def run(self) -> Optional[AdaptationResult]:
        """Adapt to the latest observed context and update introspective state."""

        if not self.state.history:
            return None

        last = self.state.history[-1]
        result = self._adapt_context(last)
        self.state.update_valence(result.details.get("valence_delta", 0.0))
        self.state.record_adaptation(result.summary)
        return result

    def _adapt_context(self, context: Any) -> AdaptationResult:
        descriptor = self.state._describe_context(context)
        novelty = self.state.meta_context.get("last_novelty_score", self.state.novelty_score(context))

        if isinstance(context, str):
            return self._adapt_text(context, novelty)

        if isinstance(context, (list, tuple, set, np.ndarray)):
            return self._adapt_sequence(context, novelty)

        if isinstance(context, dict):
            return self._adapt_mapping(context, novelty)

        if isinstance(context, (int, float)) and not isinstance(context, bool):
            return self._adapt_numeric(context, novelty)

        summary = "Processed miscellaneous context"
        details = {
            "descriptor": descriptor,
            "representation": repr(context),
            "novelty_score": novelty,
            "valence_delta": 0.004 + (0.002 * novelty),
        }
        return AdaptationResult(
            summary=summary,
            details=details,
            confidence=0.35,
            recommendations=["Provide a JSON-serializable structure for richer analysis."],
        )

    def _adapt_text(self, context: str, novelty: float) -> AdaptationResult:
        tokens = context.split()
        normalized_tokens = [token.strip(".,!?;:'\"").lower() for token in tokens]
        normalized_tokens = [token for token in normalized_tokens if token]
        unique_tokens = len(set(normalized_tokens)) if normalized_tokens else 0
        lexical_diversity = unique_tokens / len(normalized_tokens) if normalized_tokens else 0.0
        positive_hits = sum(token in self.POSITIVE_MARKERS for token in normalized_tokens)
        negative_hits = sum(token in self.NEGATIVE_MARKERS for token in normalized_tokens)
        sentiment_hint = positive_hits - negative_hits

        details = {
            "descriptor": "text",
            "transformation": "tokenize/reverse/sentiment-hint",
            "token_count": len(tokens),
            "unique_tokens": unique_tokens,
            "lexical_diversity": round(lexical_diversity, 4),
            "sentiment_hint": sentiment_hint,
            "reversed": context[::-1],
            "novelty_score": novelty,
            "valence_delta": 0.012 + (0.015 * lexical_diversity) + (0.006 * sentiment_hint),
        }
        recommendations = [
            "Keep text concise and specific for higher-confidence adaptation.",
            "Add structured fields when you need machine-readable follow-up actions.",
        ]
        confidence = min(0.95, 0.45 + (0.3 * lexical_diversity) + (0.1 * novelty))
        return AdaptationResult(
            summary="Processed textual context with lexical and sentiment signals",
            details=details,
            confidence=confidence,
            recommendations=recommendations,
        )

    def _adapt_sequence(self, context: Iterable[Any], novelty: float) -> AdaptationResult:
        sequence = list(context)
        numeric = self._is_numeric_sequence(sequence)
        mean_value = float(np.mean(sequence)) if sequence and numeric else None
        std_value = float(np.std(sequence)) if sequence and numeric else None
        entropy = self._sequence_entropy(sequence)

        details = {
            "descriptor": "sequence",
            "transformation": "profile/reverse/statistics",
            "length": len(sequence),
            "mean": mean_value,
            "standard_deviation": std_value,
            "entropy": round(entropy, 4),
            "reversed": list(reversed(sequence)),
            "novelty_score": novelty,
            "valence_delta": 0.01 + (0.005 * min(entropy, 1.0)),
        }
        recommendations = ["Normalize sequence lengths before comparing batches."]
        if numeric:
            recommendations.append("Track mean and standard deviation drift over time.")
        confidence = 0.7 if numeric else 0.55
        return AdaptationResult(
            summary="Processed sequence context with distribution metrics",
            details=details,
            confidence=confidence + (0.05 * novelty),
            recommendations=recommendations,
        )

    def _adapt_mapping(self, context: Dict[Any, Any], novelty: float) -> AdaptationResult:
        keys = list(context.keys())
        value_types = {str(key): type(value).__name__ for key, value in context.items()}
        missing_like = [key for key, value in context.items() if value in (None, "")]

        details = {
            "descriptor": "mapping",
            "transformation": "schema-profile",
            "keys": keys,
            "values": list(context.values()),
            "value_types": value_types,
            "missing_like_keys": missing_like,
            "field_count": len(keys),
            "novelty_score": novelty,
            "valence_delta": 0.012 + (0.002 * len(keys)) - (0.003 * len(missing_like)),
        }
        recommendations = ["Preserve stable key names so adaptation history stays comparable."]
        if missing_like:
            recommendations.append("Fill missing-like fields to improve downstream confidence.")
        confidence = min(0.92, 0.55 + (0.04 * len(keys)) + (0.04 * novelty))
        return AdaptationResult(
            summary="Processed mapping context with schema diagnostics",
            details=details,
            confidence=confidence,
            recommendations=recommendations,
        )

    def _adapt_numeric(self, context: float, novelty: float) -> AdaptationResult:
        normalized = self._normalize_numeric(context)
        magnitude = abs(float(context))
        details = {
            "descriptor": "numeric",
            "value": context,
            "normalized": normalized,
            "magnitude": magnitude,
            "sign": "positive" if context > 0 else "negative" if context < 0 else "zero",
            "novelty_score": novelty,
            "valence_delta": 0.008 + (0.004 * novelty),
        }
        return AdaptationResult(
            summary="Processed numeric context with normalization metrics",
            details=details,
            confidence=0.82,
            recommendations=["Compare normalized values when inputs span different scales."],
        )

    @staticmethod
    def _is_numeric_sequence(sequence: Iterable[Any]) -> bool:
        return all(isinstance(item, (int, float)) and not isinstance(item, bool) for item in sequence)

    @staticmethod
    def _normalize_numeric(value: float) -> float:
        return float(1 / (1 + np.exp(-value)))

    @staticmethod
    def _sequence_entropy(sequence: List[Any]) -> float:
        if not sequence:
            return 0.0
        counts: Dict[str, int] = {}
        for item in sequence:
            key = repr(item)
            counts[key] = counts.get(key, 0) + 1
        total = len(sequence)
        return -sum((count / total) * log2(count / total) for count in counts.values())
