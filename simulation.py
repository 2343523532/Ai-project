"""Utility script that demonstrates the adaptive agent in action."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable, List

if __package__:
    from .core import AdaptiveAgent
else:
    ROOT = Path(__file__).resolve().parent
    sys.path.append(str(ROOT))
    from core import AdaptiveAgent


def run_demo(inputs: Iterable[object], *, save_state: str | None = None) -> None:
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

    if save_state:
        agent.save_state(save_state)
        print(f"State saved to {save_state}")


def parse_context(raw_value: str) -> object:
    """Parse a single context value from JSON with string fallback."""

    try:
        return json.loads(raw_value)
    except json.JSONDecodeError:
        return raw_value


def load_inputs_from_file(filepath: str) -> List[object]:
    """Load contexts from a JSON file.

    The file can be either:
    - a JSON array of contexts, or
    - newline-delimited JSON/text entries.
    """

    path = Path(filepath)
    content = path.read_text(encoding="utf-8").strip()
    if not content:
        return []

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        parsed = [parse_context(line) for line in content.splitlines() if line.strip()]
        return parsed

    if isinstance(parsed, list):
        return parsed

    raise ValueError("Input file must contain a JSON array or newline-delimited entries.")


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
            ctx = parse_context(user_input)

            result = agent.process(ctx)
            print("Adaptation Summary:", result["adaptation_summary"])
            print("Processed Context:")
            print(json.dumps(result["processed_context"], indent=2, default=str))
            print("Reflection:", result["reflection"])
            print("Meta-state:")
            print(json.dumps(result["meta_state"], indent=2, default=str))
            print("---")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the adaptive cognitive framework demo.")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument(
        "--input-file",
        help="Path to a file containing demo contexts (JSON array or newline-delimited entries)",
    )
    parser.add_argument(
        "--save-state",
        help="Optional path to save final state after demo mode completes",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.interactive:
        run_interactive()
        return

    if args.input_file:
        demo_inputs = load_inputs_from_file(args.input_file)
    else:
        demo_inputs = [
            "First context",
            [1, 2, 3, 4],
            "Another experience to analyze",
            {"signal": 42, "status": "stable"},
            7,
        ]
    run_demo(demo_inputs, save_state=args.save_state)


if __name__ == "__main__":
    main()
