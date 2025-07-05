# Allow running as a standalone script without package context
from core import AdaptiveAgent

def main():
    agent = AdaptiveAgent()
    demo_inputs = ["First context", [1, 2, 3], "Another experience", {"signal": 42}]

    for ctx in demo_inputs:
        result = agent.process(ctx)
        print("Processed:", result["processed_context"])
        print("Reflection:", result["reflection"])
        print("Meta-state:", result["meta_state"])
        print("---")

if __name__ == "__main__":
    main()
