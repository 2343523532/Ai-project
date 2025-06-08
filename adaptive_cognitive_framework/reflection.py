class ReflectiveProcessor:
    def __init__(self, state):
        self.state = state

    def reflect(self):
        # Simulate a feedback loop
        if self.state.history:
            summary = f"Contexts observed: {len(self.state.history)}"
            valence = self.state.emotional_valence
            score = self.state.performance_score
            # Access average_context_complexity from the report
            avg_complexity = self.state.report().get('average_context_complexity', 0) # Default to 0 if somehow not in report
            return (f"System has reflected on {summary}. "
                    f"Current valence: {valence:.2f}. "
                    f"Performance score: {score:.2f}. "
                    f"Avg. context complexity: {avg_complexity:.2f}.")
        return "No context to reflect on."
