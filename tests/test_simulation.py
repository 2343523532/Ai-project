import json
import os
import tempfile

from simulation import load_inputs_from_file, parse_context


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
