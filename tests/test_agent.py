import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_NAME = "adaptive_cognitive_framework"


def _load_package() -> None:
    if PACKAGE_NAME in sys.modules:
        return

    package_spec = importlib.util.spec_from_file_location(
        f"{PACKAGE_NAME}.__init__",
        ROOT / "__init__.py",
        submodule_search_locations=[str(ROOT)],
    )
    if not package_spec or not package_spec.loader:
        raise RuntimeError("Unable to prepare package spec for adaptive framework")

    package = importlib.util.module_from_spec(package_spec)
    sys.modules[PACKAGE_NAME] = package
    package_spec.loader.exec_module(package)


def _load_module(module: str):
    _load_package()
    spec = importlib.util.spec_from_file_location(
        f"{PACKAGE_NAME}.{module}",
        ROOT / f"{module}.py",
    )
    if not spec or not spec.loader:
        raise RuntimeError(f"Unable to load module {module}")
    module_obj = importlib.util.module_from_spec(spec)
    sys.modules[f"{PACKAGE_NAME}.{module}"] = module_obj
    spec.loader.exec_module(module_obj)
    return module_obj


AdaptiveAgent = _load_module("core").AdaptiveAgent


def test_agent_process_structure():
    agent = AdaptiveAgent()
    result = agent.process("test input")

    assert set(result.keys()) == {
        "processed_context",
        "adaptation_summary",
        "reflection",
        "meta_state",
    }

    assert isinstance(result["processed_context"], dict)
    assert result["adaptation_summary"]
    assert "valence" in result["reflection"].lower()

    meta_state = result["meta_state"]
    assert meta_state["history_length"] == 1
    assert meta_state["recent_context_descriptor"] == "text"

    # Ensure JSON serialization works for the processed context
    json.dumps(result["processed_context"], default=str)


def test_agent_handles_various_inputs():
    agent = AdaptiveAgent()
    contexts = ["text", [1, 2, 3], {"value": 1}, 3.14]

    for ctx in contexts:
        result = agent.process(ctx)
        assert result["adaptation_summary"].startswith("Processed")
        assert "valence" in result["reflection"].lower()
        assert result["meta_state"]["history_length"] >= 1
