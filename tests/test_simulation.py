import json
import os
import tempfile

from simulation import load_inputs_from_file, parse_context, summarize_results


def test_parse_context_json_and_text():
    assert parse_context('{"a": 1}') == {"a": 1}
    assert parse_context("plain text") == "plain text"


def test_load_inputs_from_json_array_file():
    with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".json") as tmp:
        json.dump(["hello", {"k": "v"}, 3], tmp)
        tmp_path = tmp.name

    try:
        result = load_inputs_from_file(tmp_path)
        assert result == ["hello", {"k": "v"}, 3]
    finally:
        os.remove(tmp_path)


def test_load_inputs_from_newline_file():
    with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".txt") as tmp:
        tmp.write('{"x": 1}\n')
        tmp.write('plain\n')
        tmp.write('[1,2]\n')
        tmp_path = tmp.name

    try:
        result = load_inputs_from_file(tmp_path)
        assert result == [{"x": 1}, "plain", [1, 2]]
    finally:
        os.remove(tmp_path)


def test_summarize_results_handles_empty_and_populated_inputs():
    empty_summary = summarize_results([])
    assert empty_summary["total_steps"] == 0
    assert empty_summary["last_adaptation_summary"] is None
    assert empty_summary["average_confidence"] == 0.0

    populated_summary = summarize_results(
        [
            {
                "adaptation_summary": "Processed text",
                "meta_state": {"history_length": 1},
                "adaptation": {"confidence": 0.4},
            },
            {
                "adaptation_summary": "Processed list",
                "meta_state": {"history_length": 2},
                "adaptation": {"confidence": 0.8},
            },
        ]
    )

    assert populated_summary == {
        "total_steps": 2,
        "last_adaptation_summary": "Processed list",
        "final_history_length": 2,
        "average_confidence": 0.6,
    }
