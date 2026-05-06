if __package__:
    from .introspection import IntrospectiveState
    from .adaptation import AdaptiveLoop
    from .reflection import ReflectiveProcessor
else:
    from introspection import IntrospectiveState
    from adaptation import AdaptiveLoop
    from reflection import ReflectiveProcessor


class AdaptiveAgent:
    """High-level facade that orchestrates observation, adaptation, and reflection."""

    def __init__(self):
        self.state = IntrospectiveState()
        self.adaptive_loop = AdaptiveLoop(self.state)
        self.reflective_processor = ReflectiveProcessor(self.state)

    def process(self, input_context):
        """Process one input context and return a structured lifecycle report."""

        self.state.observe(input_context)
        adaptation = self.adaptive_loop.run()
        reflection = self.reflective_processor.reflect(adaptation)
        return {
            "processed_context": adaptation.details if adaptation else None,
            "adaptation_summary": adaptation.summary if adaptation else None,
            "adaptation": adaptation.to_dict() if adaptation else None,
            "reflection": reflection,
            "meta_state": self.state.report(),
        }

    def process_batch(self, contexts):
        """Process a sequence of contexts and return all results."""

        return [self.process(ctx) for ctx in contexts]

    def diagnose(self) -> dict:
        """Return a compact health report for monitoring and UI integrations."""

        report = self.state.report()
        return {
            "history_length": report["history_length"],
            "dominant_context_type": report["dominant_context_type"],
            "cognitive_load": report["cognitive_load"],
            "valence_trend": report["valence_trend"],
            "recommendation": self.reflective_processor._recommend_next_focus(
                report, None
            ),
        }

    def reset_state(self) -> None:
        """Reset the agent to a fresh introspective state."""
        self.state = IntrospectiveState()
        self.adaptive_loop = AdaptiveLoop(self.state)
        self.reflective_processor = ReflectiveProcessor(self.state)

    def get_state_snapshot(self) -> dict:
        """Return a serializable snapshot of the current internal state."""
        return self.state.to_dict()

    def save_state(self, filepath: str) -> None:
        """Save the agent's internal state to a file."""
        import json

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.state.to_dict(), f, default=str, indent=2)

    def load_state(self, filepath: str) -> None:
        """Load the agent's internal state from a file."""
        import json

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.state.load_from_dict(data)
