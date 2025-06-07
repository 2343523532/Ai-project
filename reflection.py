class ReflectiveProcessor:
    def __init__(self, state):
        self.state = state

    def reflect(self):
        # Simulate a feedback loop
        if self.state.history:
            summary = f"Contexts observed: {len(self.state.history)}"
            valence = self.state.emotional_valence
            return f"System has reflected on {summary}, current valence: {valence:.2f}"
        return "No context to reflect on."
