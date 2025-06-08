from .core import AdaptiveAgent

def main():
    agent = AdaptiveAgent()
    demo_inputs = [
        "Short string",       # Tests string adaptation (target length 10)
        50,                   # Tests number adaptation (target value 100)
        "A much longer string that will be truncated", # Tests string truncation
        120,                  # Tests number adaptation (decrementing)
        "This is a harmful test", # Tests ethical layer (unsafe keyword)
        {"data": "some complex data", "value": 75}, # Tests non-string/number context & complexity
        "safe string"         # Another safe string
    ]

    for i, ctx in enumerate(demo_inputs):
        print(f"--- Input {i+1}: {ctx} ---")
        result = agent.process(ctx)

        print(f"Safety Check: {result.get('safety_check', 'N/A')}")
        if result.get('safety_check') == 'failed':
            print(f"Processed Context/Action: {result.get('processed_context', 'N/A')}") # Should be None
            print(f"Reflection: {result['reflection']}")
        else:
            print(f"Processed Context/Action: {result['processed_context']}")
            print(f"Reflection: {result['reflection']}")

        # Meta-state now contains performance_score and avg_complexity
        print(f"Meta-state: {result['meta_state']}")
        print("\n")

if __name__ == "__main__":
    main()
