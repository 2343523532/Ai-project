import numpy as np

class IntrospectiveState:
    def __init__(self):
        self.history = []
        self.meta_context = {}
        self.emotional_valence = 0.0  # Placeholder
        self.performance_score = 0.0
        self.total_context_complexity = 0

    def observe(self, context):
        self.history.append(context)
        # Meta-context analysis (placeholder logic)
        self.meta_context['last'] = context
        # Calculate complexity
        if isinstance(context, (str, list)):
            complexity = len(context)
        elif isinstance(context, dict):
            complexity = len(context.keys())
        else:
            complexity = 1
        self.total_context_complexity += complexity

    def report(self):
        if self.history:
            average_context_complexity = self.total_context_complexity / len(self.history)
        else:
            average_context_complexity = 0
        return {
            "history_length": len(self.history),
            "recent_context": self.meta_context.get('last', None),
            "emotional_valence": self.emotional_valence,
            'performance_score': self.performance_score,
            'average_context_complexity': average_context_complexity,
        }
