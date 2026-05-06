if __package__:
    from .introspection import IntrospectiveState
    from .adaptation import AdaptiveLoop
    from .reflection import ReflectiveProcessor
else:
    from introspection import IntrospectiveState
    from adaptation import AdaptiveLoop
    from reflection import ReflectiveProcessor

class AdaptiveAgent:
    """High-level orchestrator for observation, adaptation, and reflection."""

    def __init__(self):
        self.state = IntrospectiveState()
        self.adaptive_loop = AdaptiveLoop(self.state)
        self.reflective_processor = ReflectiveProcessor(self.state)

    def process(self, input_context):
        """Process one context and return a structured cognitive cycle report."""

        self.state.observe(input_context)
        adaptation = self.adaptive_loop.run()
        reflection = self.reflective_processor.reflect(adaptation)
        adaptation_payload = adaptation.to_dict() if adaptation else None
        return {
            "processed_context": adaptation.details if adaptation else None,
            "adaptation_summary": adaptation.summary if adaptation else None,
            "adaptation": adaptation_payload,
            "reflection": reflection,
            "meta_state": self.state.report(),
            "recommendations": adaptation.recommendations if adaptation else [],
        }

    def process_batch(self, contexts):
        """Process a sequence of contexts and return all results."""
        return [self.process(ctx) for ctx in contexts]

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
        with open(filepath, 'w') as f:
            json.dump(self.state.to_dict(), f, default=str, indent=2)

    def load_state(self, filepath: str) -> None:
        """Load the agent's internal state from a file."""
        import json
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.state.load_from_dict(data)
