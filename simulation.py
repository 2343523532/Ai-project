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


def main() -> None:
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
