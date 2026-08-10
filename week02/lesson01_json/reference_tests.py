"""W2-01 参考实现测试。"""

import json
from pathlib import Path

import pytest
from reference_solution import (
    build_research_record,
    load_json,
    save_record,
    serialize_record,
)

INVALID_JSON_PATH = (
    Path(__file__).resolve().parent / "data" / "invalid_research_record.json"
)


def test_build_research_record_uses_json_compatible_types() -> None:
    record = build_research_record()

    assert record["sample_size"] == 240
    assert isinstance(record["statistical_methods"], list)
    assert record["peer_reviewed"] is True
    assert record["notes"] is None


def test_serialize_record_preserves_chinese_and_adds_indentation() -> None:
    record = build_research_record()

    json_text = serialize_record(record)

    assert json.loads(json_text) == record
    assert "睡眠时长" in json_text
    assert '\n  "title"' in json_text


def test_save_and_load_record_round_trip(tmp_path: Path) -> None:
    record = build_research_record()
    output_path = tmp_path / "record.json"

    save_record(record, output_path)

    assert load_json(output_path) == record
    assert "睡眠时长" in output_path.read_text(encoding="utf-8")


def test_load_json_propagates_decode_error() -> None:
    with pytest.raises(json.JSONDecodeError):
        load_json(INVALID_JSON_PATH)
