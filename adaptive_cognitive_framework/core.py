from __future__ import annotations
from typing import Any, Dict

from .introspection import IntrospectiveState
from .adaptation import AdaptiveLoop
from .reflection import ReflectiveProcessor


class AdaptiveAgent:
    def __init__(self) -> None:
        self.state = IntrospectiveState()
        self.adaptive_loop = AdaptiveLoop(self.state)
        self.reflective_processor = ReflectiveProcessor(self.state)

    def process(self, input_context: Any) -> Dict[str, Any]:
        self.state.observe(input_context)
        adaptation = self.adaptive_loop.run()
        reflection = self.reflective_processor.reflect(adaptation)
        return {
            "processed_context": adaptation.details if adaptation else None,
            "adaptation_summary": adaptation.summary if adaptation else None,
            "reflection": reflection,
            "meta_state": self.state.report(),
        }

    def save_state(self, filepath: str) -> None:
        """Save the agent's internal state to a file."""
        import json

        with open(filepath, "w") as f:
            json.dump(self.state.to_dict(), f, default=str, indent=2)

    def load_state(self, filepath: str) -> None:
        """Load the agent's internal state from a file."""
        import json

        with open(filepath, "r") as f:
            data = json.load(f)
            self.state.load_from_dict(data)
