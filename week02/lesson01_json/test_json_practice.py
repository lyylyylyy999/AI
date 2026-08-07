import json
from pathlib import Path

import pytest
from json_practice import (
    build_research_record,
    load_json,
    save_record,
    serialize_record,
)


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


def test_save_record() -> None:
    record = build_research_record()
    path = Path("week02/lesson01_json/data/test.json")
    save_record(record, path)
    loaded_record = load_json(path)
    assert record == loaded_record


def test_invalid_load_json() -> None:
    path = Path("week02/lesson01_json/data/invalid_research_record.json")
    with pytest.raises(json.JSONDecodeError):
        load_json(path)
