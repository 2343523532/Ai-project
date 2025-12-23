from adaptive_cognitive_framework.core import AdaptiveAgent
import json


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
