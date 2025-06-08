from .introspection import IntrospectiveState
from .adaptation import AdaptiveLoop
from .reflection import ReflectiveProcessor

class AdaptiveAgent:
    def __init__(self):
        self.state = IntrospectiveState()
        self.adaptive_loop = AdaptiveLoop(self.state)
        self.reflective_processor = ReflectiveProcessor(self.state)
        self.unsafe_keywords = ["harmful", "danger", "attack", "exploit"]

    def is_safe(self, context):
        if isinstance(context, str):
            for keyword in self.unsafe_keywords:
                if keyword in context.lower():
                    return False
        return True

    def process(self, input_context):
        if not self.is_safe(input_context):
            return {
                "processed_context": None,
                "reflection": "Input considered unsafe. Processing halted.",
                "meta_state": self.state.report(),
                "safety_check": "failed"
            }

        self.state.observe(input_context)
        adaptation_result = self.adaptive_loop.run()
        # Ensure adaptation_result is a dictionary and unpack correctly
        processed_context = None
        if isinstance(adaptation_result, dict):
            processed_context = adaptation_result.get('action_taken')
        elif adaptation_result is not None: # Fallback if previous structure was returned
            processed_context = adaptation_result


        reflection = self.reflective_processor.reflect()
        return {
            "processed_context": processed_context,
            "reflection": reflection,
            "meta_state": self.state.report(),
            "safety_check": "passed"
        }
