import os
import tempfile
from adaptive_cognitive_framework.core import AdaptiveAgent


def test_save_load_state():
    # 1. Initialize agent and process some inputs
    agent = AdaptiveAgent()
    agent.process("test input 1")
    agent.process([1, 2, 3])

    # 2. Get current state report
    original_report = agent.state.report()
    assert original_report["history_length"] == 2

    # 3. Save state to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, mode="w+") as tmp:
        tmp_path = tmp.name

    try:
        agent.save_state(tmp_path)

        # 4. Create a new agent and load state
        new_agent = AdaptiveAgent()
        new_agent.load_state(tmp_path)

        # 5. Verify the loaded state matches the original
        loaded_report = new_agent.state.report()

        assert loaded_report["history_length"] == original_report["history_length"]
        assert (
            loaded_report["emotional_valence"] == original_report["emotional_valence"]
        )
        assert loaded_report["context_stats"] == original_report["context_stats"]
        assert (
            loaded_report["recent_adaptations"] == original_report["recent_adaptations"]
        )

        # 6. Verify history content
        assert new_agent.state.history == agent.state.history

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_persistence_preserves_deque_attributes():
    agent = AdaptiveAgent()
    agent.process("input 1")
    agent.process("input 2")

    with tempfile.NamedTemporaryFile(delete=False, mode="w+") as tmp:
        tmp_path = tmp.name

    try:
        agent.save_state(tmp_path)

        new_agent = AdaptiveAgent()
        new_agent.load_state(tmp_path)

        # Verify that deques are still deques
        assert len(new_agent.state.recent_contexts) == 2

        new_agent.process("input 3")
        assert len(new_agent.state.recent_contexts) == 3

    finally:
        os.remove(tmp_path)
