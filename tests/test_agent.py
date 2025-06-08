import pytest
import numpy as np # Though not directly used, it's in requirements and adaptation.py imports it.

from adaptive_cognitive_framework.core import AdaptiveAgent
from adaptive_cognitive_framework.introspection import IntrospectiveState
from adaptive_cognitive_framework.adaptation import AdaptiveLoop
from adaptive_cognitive_framework.reflection import ReflectiveProcessor

# Test IntrospectiveState
def test_introspective_state_init():
    state = IntrospectiveState()
    assert state.performance_score == 0.0
    assert state.total_context_complexity == 0
    assert len(state.history) == 0
    assert state.emotional_valence == 0.0

def test_introspective_state_observe():
    state = IntrospectiveState()
    state.observe("hello")
    assert len(state.history) == 1
    assert state.history[0] == "hello"
    assert state.total_context_complexity == 5 # len("hello")

    state.observe([1, 2, 3])
    assert len(state.history) == 2
    assert state.total_context_complexity == 5 + 3 # 3 for list length

    state.observe({"key": "value"})
    assert len(state.history) == 3
    assert state.total_context_complexity == 5 + 3 + 1 # 1 for dict keys

    state.observe(123) # Other type
    assert len(state.history) == 4
    assert state.total_context_complexity == 5 + 3 + 1 + 1 # 1 for other type

def test_introspective_state_report():
    state = IntrospectiveState()
    state.observe("hi")
    state.observe([1,2,3,4])
    state.performance_score = 7.5

    report = state.report()
    assert report['history_length'] == 2
    assert report['recent_context'] == [1,2,3,4]
    assert report['performance_score'] == 7.5
    assert report['average_context_complexity'] == (2 + 4) / 2 # (len("hi") + len([1,2,3,4])) / 2

# Test AdaptiveLoop
def test_adaptive_loop_init():
    state = IntrospectiveState()
    loop = AdaptiveLoop(state)
    assert loop.target_number == 100
    assert loop.target_string_length == 10

def test_adaptive_loop_run_number_increase():
    state = IntrospectiveState()
    loop = AdaptiveLoop(state)
    state.observe(50)
    result = loop.run()
    assert result['action_taken'] == 51 # Incrementing by 1
    assert result['action_score'] > 0 # Score should be positive
    assert state.performance_score == result['action_score']
    assert state.emotional_valence > 0

def test_adaptive_loop_run_number_decrease():
    state = IntrospectiveState()
    loop = AdaptiveLoop(state)
    state.observe(150)
    result = loop.run()
    assert result['action_taken'] == 149 # Decrementing by 1
    assert result['action_score'] > 0 # Score should be positive for getting closer
    assert state.performance_score == result['action_score']

def test_adaptive_loop_run_number_target_met():
    state = IntrospectiveState()
    loop = AdaptiveLoop(state)
    state.observe(100)
    result = loop.run()
    assert result['action_taken'] == 100 # Stays at target
    assert result['action_score'] == 0 # No change, no score
    assert state.performance_score == 0

def test_adaptive_loop_run_string_increase():
    state = IntrospectiveState()
    loop = AdaptiveLoop(state)
    state.observe("short") # len 5
    result = loop.run()
    assert result['action_taken'] == "shorta" # Appends "a"
    assert result['action_score'] == 1 # len("shorta") - len("short")
    assert state.performance_score == 1

def test_adaptive_loop_run_string_target_met_or_exceeded():
    state = IntrospectiveState()
    loop = AdaptiveLoop(state)
    # Target length is 10
    state.observe("longstring") # len 10
    result = loop.run()
    assert result['action_taken'] == "longstring" # No change
    assert result['action_score'] == 0

    # Reset state for the next observation
    state.history = [] # Clear history to observe fresh
    state.total_context_complexity = 0
    state.performance_score = 0 # Reset score for isolated test observation

    state.observe("verylongstring") # len 14
    result_long = loop.run()
    # Actual implemented logic is last_context[:-1]
    # "verylongstring" (14) -> "verylongstrin" (13)
    assert result_long['action_taken'] == "verylongstrin"
    assert len(result_long['action_taken']) == 13
    assert result_long['action_score'] == 0 # Score is 0 because length did not increase

def test_adaptive_loop_run_other_type():
    state = IntrospectiveState()
    loop = AdaptiveLoop(state)
    state.observe({"a": 1})
    result = loop.run()
    assert result['action_taken'] == {"a": 1}
    assert result['action_score'] == 0

# Test Ethical Layer (in AdaptiveAgent)
def test_agent_ethical_layer_safe_input():
    agent = AdaptiveAgent()
    result = agent.process("This is a safe message.")
    assert result['safety_check'] == "passed"
    assert result['processed_context'] is not None

def test_agent_ethical_layer_unsafe_input():
    agent = AdaptiveAgent()
    # Using one of the default unsafe keywords
    result = agent.process("This message contains harmful content.")
    assert result['safety_check'] == "failed"
    assert result['processed_context'] is None
    assert "unsafe" in result['reflection'].lower()

def test_agent_ethical_layer_case_insensitivity():
    agent = AdaptiveAgent()
    result = agent.process("This message contains DANGER.") # Uppercase
    assert result['safety_check'] == "failed"
    assert result['processed_context'] is None

def test_agent_ethical_layer_non_string_input():
    agent = AdaptiveAgent()
    result = agent.process(12345)
    assert result['safety_check'] == "passed" # Non-strings are safe by default

# Test AdaptiveAgent process flow
def test_agent_process_flow_normal():
    agent = AdaptiveAgent()
    input_context = "Initialize context" # len 18
    result = agent.process(input_context)

    assert result['safety_check'] == "passed"
    # processed_context should be the result of adaptation
    # "Initialize context" (len 18) is truncated by last_context[:-1] to "Initialize contex" (len 17)
    assert result['processed_context'] == "Initialize contex"
    assert len(result['processed_context']) == 17


    assert "reflected on" in result['reflection'].lower()
    meta_state = result['meta_state']
    assert meta_state['history_length'] == 1
    assert meta_state['recent_context'] == input_context
    # performance_score for truncation from 18 to 10.
    # Score rule: len(action_taken) - len(last_context) if length increased towards target, else 0.
    # 10 - 18 = -8. Not "increased". So score = 0.
    assert meta_state['performance_score'] == 0
    assert meta_state['average_context_complexity'] == len(input_context)

def test_agent_process_flow_multiple_inputs():
    agent = AdaptiveAgent()
    agent.process("first") # len 5 -> "firsta" (len 6). Score = 1. Perf_score = 1.
    agent.process(10)    # 10 -> 11. Score = abs(100-10)-abs(100-11) = 90-89 = 1. Perf_score = 1+1=2.
    result = agent.process("second harmful input") # Unsafe

    assert result['safety_check'] == "failed"
    meta_state = result['meta_state']
    assert meta_state['history_length'] == 2 # Unsafe input is not added to history
    assert meta_state['recent_context'] == 10 # Last safe context
    assert meta_state['performance_score'] == 2.0


# Test ReflectiveProcessor (implicitly tested via agent, but direct check is good)
def test_reflective_processor():
    state = IntrospectiveState()
    ref_processor = ReflectiveProcessor(state)
    assert ref_processor.reflect() == "No context to reflect on."

    state.observe("test context") # len 12
    state.performance_score = 5.5
    # total_context_complexity = len("test context") = 12
    # avg_context_complexity = 12 / 1 = 12.0

    reflection = ref_processor.reflect()
    assert "Contexts observed: 1" in reflection
    assert "Performance score: 5.50" in reflection
    assert f"Avg. context complexity: {12.0:.2f}" in reflection
