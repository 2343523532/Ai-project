import numpy as np

class AdaptiveLoop:
    def __init__(self, state):
        self.state = state
        self.target_number = 100
        self.target_string_length = 10

    def run(self):
        action_taken = None
        action_score = 0.0
        result = None

        if self.state.history:
            last_context = self.state.history[-1]
            result = last_context # Default result

            if isinstance(last_context, (int, float)):
                step = 1 if isinstance(last_context, int) else 0.1
                if last_context < self.target_number:
                    action_taken = last_context + step
                elif last_context > self.target_number:
                    action_taken = last_context - step
                else:
                    action_taken = last_context # No change needed

                # Ensure action_taken does not overshoot if it's close
                if abs(last_context - self.target_number) < step and last_context != self.target_number:
                     action_taken = self.target_number

                action_score = abs(self.target_number - last_context) - abs(self.target_number - action_taken)
                result = action_taken

            elif isinstance(last_context, str):
                if len(last_context) < self.target_string_length:
                    action_taken = last_context + "a"
                    action_score = len(action_taken) - len(last_context)
                elif len(last_context) > self.target_string_length:
                    action_taken = last_context[:-1] # Truncate
                    action_score = 0 # Or some other logic for truncation
                else:
                    action_taken = last_context # No change
                    action_score = 0
                result = action_taken

            else: # Other types
                action_taken = last_context
                action_score = 0.0
                result = last_context

            self.state.performance_score += action_score
            if action_score > 0:
                self.state.emotional_valence += 0.01 * action_score
            elif action_score < 0:
                self.state.emotional_valence -= 0.01 * abs(action_score)

            return {'action_taken': result, 'action_score': action_score}

        return {'action_taken': result, 'action_score': action_score}
