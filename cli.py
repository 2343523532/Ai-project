import argparse
from core import AdaptiveAgent


def main():
    """Run the AdaptiveAgent from the command line."""
    parser = argparse.ArgumentParser(description="Run adaptive agent with custom contexts")
    parser.add_argument("contexts", nargs="+", help="Contexts to process in sequence")
    args = parser.parse_args()

    agent = AdaptiveAgent()
    for ctx in args.contexts:
        result = agent.process(ctx)
        print("Processed:", result["processed_context"])
        print("Reflection:", result["reflection"])
        print("Meta-state:", result["meta_state"])
        print("---")


if __name__ == "__main__":
    main()
