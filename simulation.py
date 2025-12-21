"""Utility script that demonstrates the adaptive agent in action."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Iterable

if __package__:
    from .core import AdaptiveAgent
else:
    ROOT = Path(__file__).resolve().parent
    sys.path.append(str(ROOT))
    from core import AdaptiveAgent


def run_demo(inputs: Iterable[object]) -> None:
    agent = AdaptiveAgent()

    for index, ctx in enumerate(inputs, start=1):
        result = agent.process(ctx)
        print(f"Step {index}")
        print("Input:", ctx)
        print("Adaptation Summary:", result["adaptation_summary"])
        print("Processed Context:")
        print(json.dumps(result["processed_context"], indent=2, default=str))
        print("Reflection:", result["reflection"])
        print("Meta-state:")
        print(json.dumps(result["meta_state"], indent=2, default=str))
        print("---")


def run_interactive() -> None:
    agent = AdaptiveAgent()
    print("Interactive Mode. Type input or commands (/save <file>, /load <file>, /quit)")

    while True:
        try:
            user_input = input(">> ")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting interactive mode.")
            break

        if not user_input.strip():
            continue

        if user_input.startswith("/quit") or user_input.startswith("/exit"):
            break
        elif user_input.startswith("/save "):
            filepath = user_input.split(" ", 1)[1]
            try:
                agent.save_state(filepath)
                print(f"State saved to {filepath}")
            except Exception as e:
                print(f"Error saving state: {e}")
        elif user_input.startswith("/load "):
            filepath = user_input.split(" ", 1)[1]
            try:
                agent.load_state(filepath)
                print(f"State loaded from {filepath}")
            except Exception as e:
                print(f"Error loading state: {e}")
        else:
            # Try to parse input as JSON, else treat as string
            try:
                ctx = json.loads(user_input)
            except json.JSONDecodeError:
                ctx = user_input

            result = agent.process(ctx)
            print("Adaptation Summary:", result["adaptation_summary"])
            print("Processed Context:")
            print(json.dumps(result["processed_context"], indent=2, default=str))
            print("Reflection:", result["reflection"])
            print("Meta-state:")
            print(json.dumps(result["meta_state"], indent=2, default=str))
            print("---")


def main() -> None:
    if "--interactive" in sys.argv:
        run_interactive()
        return

    demo_inputs = [
        "First context",
        [1, 2, 3, 4],
        "Another experience to analyze",
        {"signal": 42, "status": "stable"},
        7,
    ]
    run_demo(demo_inputs)

if __name__ == "__main__":
    main()
