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
        "adaptation",
        "reflection",
        "meta_state",
    }

    assert isinstance(result["processed_context"], dict)
    assert result["adaptation_summary"]
    assert result["adaptation"]["strategy"] == "text-lexical-profiler"
    assert result["adaptation"]["confidence"] > 0
    assert "valence" in result["reflection"].lower()

    meta_state = result["meta_state"]
    assert meta_state["history_length"] == 1
    assert meta_state["recent_context_descriptor"] == "text"
    assert meta_state["dominant_context_type"] == "text"
    assert "cognitive_load" in meta_state

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


def test_agent_batch_snapshot_and_reset():
    agent = AdaptiveAgent()
    results = agent.process_batch(["one", {"x": 1}, [1, 2]])

    assert len(results) == 3
    assert results[-1]["meta_state"]["history_length"] == 3

    snapshot = agent.get_state_snapshot()
    assert "history" in snapshot
    assert len(snapshot["history"]) == 3

    agent.reset_state()
    post_reset = agent.state.report()
    assert post_reset["history_length"] == 0


def test_agent_exposes_richer_adaptation_metrics():
    agent = AdaptiveAgent()

    text_result = agent.process("alpha beta beta gamma")
    assert text_result["processed_context"]["repeated_terms"] == ["beta"]
    assert "repetition_detected" in text_result["adaptation"]["signals"]

    sequence_result = agent.process([1, 2, 3, 4])
    assert sequence_result["processed_context"]["is_numeric"] is True
    assert sequence_result["processed_context"]["median"] == 2.5

    mapping_result = agent.process({"a": 1, "nested": [1, 2]})
    assert mapping_result["processed_context"]["nested_keys"] == ["nested"]
    assert "sequence->mapping" in mapping_result["meta_state"]["transition_counts"]


def test_agent_diagnose_returns_health_snapshot():
    agent = AdaptiveAgent()
    agent.process("diagnostic input")

    diagnosis = agent.diagnose()

    assert diagnosis["history_length"] == 1
    assert diagnosis["dominant_context_type"] == "text"
    assert diagnosis["recommendation"]
