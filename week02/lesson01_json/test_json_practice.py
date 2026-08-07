import json
from pathlib import Path

import pytest
from json_practice import (
    build_research_record,
    load_json,
    save_record,
    serialize_record,
)

INVALID_PATH = Path(__file__).resolve().parent / "data" / "invalid_research_record.json"


def test_build_research_record() -> None:
    record = build_research_record()
    assert record["remarks"] is None
    assert isinstance(record["peer_review"], bool)
    assert isinstance(record["stat_method"], list)


def test_serialize_record() -> None:
    record = build_research_record()
    json_text = serialize_record(record)
    record_result = json.loads(json_text)
    assert record == record_result
    assert "贝叶斯" in json_text
    assert "\n" in json_text


def test_save_record(tmp_path: Path) -> None:
    record = build_research_record()
    test_path = tmp_path / "test.json"
    save_record(record, test_path)
    loaded_record = load_json(test_path)
    assert record == loaded_record


def test_invalid_load_json() -> None:
    path = INVALID_PATH
    with pytest.raises(json.JSONDecodeError):
        load_json(path)
