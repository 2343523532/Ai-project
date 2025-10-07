if __package__:
    from .introspection import IntrospectiveState
    from .adaptation import AdaptiveLoop
    from .reflection import ReflectiveProcessor
else:
    from introspection import IntrospectiveState
    from adaptation import AdaptiveLoop
    from reflection import ReflectiveProcessor

class AdaptiveAgent:
    def __init__(self):
        self.state = IntrospectiveState()
        self.adaptive_loop = AdaptiveLoop(self.state)
        self.reflective_processor = ReflectiveProcessor(self.state)

    def process(self, input_context):
        self.state.observe(input_context)
        adaptation = self.adaptive_loop.run()
        reflection = self.reflective_processor.reflect(adaptation)
        return {
            "processed_context": adaptation.details if adaptation else None,
            "adaptation_summary": adaptation.summary if adaptation else None,
            "reflection": reflection,
            "meta_state": self.state.report()
        }
