import json
import traceback
from io import StringIO
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.domain import InvalidMessageError, Message, Statistics, summarize
from app.jsonl import parse_lines, read_jsonl


def record(**changes: object) -> str:
    data: dict[str, object] = {
        "conversation_id": "a", "role": "user", "content": "正文",
    }
    data.update(changes)
    return json.dumps(data, ensure_ascii=False)


def test_statistics_preserve_order_original_content_and_conversation_ids():
    contents = [" 系统\n", "你好🙂", "回答  ", "再次提问"]
    lines = iter([
        record(role="system", content=contents[0]),
        " \t\n",
        record(content=contents[1]),
        record(conversation_id="b", role="assistant", content=contents[2]),
        record(content=contents[3]),
    ])
    messages = list(parse_lines(lines))
    assert [message.content for message in messages] == contents
    assert [message.conversation_id for message in messages] == ["a", "a", "b", "a"]
    assert summarize(iter(messages)).model_dump() == {
        "total_messages": 4,
        "conversation_count": 2,
        "messages_by_role": {"system": 1, "user": 2, "assistant": 1},
        "total_characters": sum(map(len, contents)),
    }


@pytest.mark.parametrize("lines", [[], ["\n", " \t\n"]])
def test_empty_input_produces_complete_zero_statistics(lines):
    assert summarize(parse_lines(iter(lines))).model_dump() == {
        "total_messages": 0, "conversation_count": 0,
        "messages_by_role": {"system": 0, "user": 0, "assistant": 0},
        "total_characters": 0,
    }


@pytest.mark.parametrize(("line", "code"), [
    ('{"secret-marker":', "invalid_json"),
    ('["secret-marker"]', "not_object"),
    ('{"content":"secret-marker"}', "missing_fields"),
    (record(**{"secret-marker": "private"}), "extra_fields"),
    (record(conversation_id=4, content="secret-marker"), "invalid_type"),
    (record(role=False, content="secret-marker"), "invalid_type"),
    (record(content=["secret-marker"]), "invalid_type"),
    (record(role="secret-marker"), "invalid_role"),
    (record(content=" \t\n"), "blank_value"),
    (record(conversation_id=" \t", content="secret-marker"), "blank_value"),
])
def test_invalid_record_has_physical_line_category_and_safe_traceback(line, code):
    with pytest.raises(InvalidMessageError) as captured:
        list(parse_lines(iter(["\n", " \n", line])))
    error = captured.value
    assert error.code == code
    assert error.line_number == 3
    assert "第3行" in str(error)
    assert "secret-marker" not in str(error)
    formatted = "".join(traceback.format_exception(error))
    assert "secret-marker" not in formatted


@pytest.mark.parametrize(("changes", "code"), [
    ({"conversation_id": None}, "string_type"),
    ({"role": "tool"}, "literal_error"),
    ({"content": " "}, "blank_value"),
])
def test_direct_message_uses_pydantic_validation(changes, code):
    data = {"conversation_id": "a", "role": "user", "content": "内容"}
    data.update(changes)
    with pytest.raises(ValidationError) as captured:
        Message.model_validate(data)
    assert captured.value.errors(include_input=False)[0]["type"] == code


@pytest.mark.parametrize(("line", "code"), [
    ('{"role":42,"extra":true}', "missing_fields"),
    (record(role=42, extra=True), "extra_fields"),
    (record(role="wrong", content=42), "invalid_type"),
    (record(role="wrong", content=" "), "invalid_role"),
])
def test_validation_priority(line, code):
    with pytest.raises(InvalidMessageError) as captured:
        list(parse_lines([line]))
    assert captured.value.code == code


def test_parsing_is_lazy_and_stops_on_first_invalid_record():
    visited: list[int] = []

    def lines():
        for index, value in enumerate([record(), "invalid", record()]):
            visited.append(index)
            yield value

    messages = parse_lines(lines())
    assert visited == []
    assert next(messages).content == "正文"
    assert visited == [0]
    with pytest.raises(InvalidMessageError, match="invalid_json"):
        next(messages)
    assert visited == [0, 1]
    with pytest.raises(StopIteration):
        next(messages)


def test_summary_does_not_return_partial_success():
    with pytest.raises(InvalidMessageError, match="invalid_json"):
        summarize(parse_lines([record(), "invalid"]))


def test_pydantic_json_roundtrip_preserves_content_and_statistics():
    message = Message(conversation_id=" a ", role="user", content=" 中文🙂\n ")
    restored = Message.model_validate_json(message.model_dump_json())
    assert restored == message
    assert restored.content == " 中文🙂\n "
    assert restored.conversation_id == " a "
    result = summarize([restored])
    assert Statistics.model_validate_json(result.model_dump_json()) == result
    assert Message.model_json_schema()["properties"]["role"]["enum"] == [
        "system", "user", "assistant",
    ]


@pytest.mark.parametrize("as_string", [True, False])
def test_file_adapter_accepts_path_or_string_and_keeps_content(tmp_path, as_string):
    path = tmp_path / "input.jsonl"
    path.write_text(record(content=" \r\n正文🙂  ") + "\n", encoding="utf-8")
    assert list(read_jsonl(str(path) if as_string else path)) == [
        Message(conversation_id="a", role="user", content=" \r\n正文🙂  "),
    ]


def test_file_adapter_preserves_missing_and_encoding_errors(tmp_path):
    with pytest.raises(FileNotFoundError):
        list(read_jsonl(tmp_path / "missing.jsonl"))
    path = tmp_path / "invalid.jsonl"
    path.write_bytes(b"\xff")
    with pytest.raises(UnicodeDecodeError):
        list(read_jsonl(path))


@pytest.mark.parametrize("exit_mode", ["exhaust", "failure", "close"])
def test_file_closed_on_exhaustion_failure_and_explicit_close(monkeypatch, exit_mode):
    stream = StringIO(record() + "\n" + ("invalid\n" if exit_mode == "failure" else ""))
    monkeypatch.setattr(Path, "open", lambda *args, **kwargs: stream)
    messages = read_jsonl("unused.jsonl")
    if exit_mode == "failure":
        with pytest.raises(InvalidMessageError, match="invalid_json"):
            list(messages)
    elif exit_mode == "close":
        next(messages)
        messages.close()
    else:
        assert len(list(messages)) == 1
    assert stream.closed
