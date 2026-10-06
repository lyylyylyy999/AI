import json
from collections.abc import Generator, Iterable, Iterator
from pathlib import Path

from pydantic import ValidationError

from app.domain import InvalidMessageError, Message


def parse_lines(lines: Iterable[str]) -> Iterator[Message]:
    """逐条产出合法消息；调用者必须完成全部迭代后才能确认整批导入成功。"""
    error_codes = {
        "missing": "missing_fields",
        "extra_forbidden": "extra_fields",
        "string_type": "invalid_type",
        "invalid_type": "invalid_type",
        "literal_error": "invalid_role",
        "blank_value": "blank_value",
    }
    priority = ["missing_fields", "extra_fields", "invalid_type", "invalid_role", "blank_value"]
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            raise InvalidMessageError("invalid_json", line_number) from None
        if not isinstance(data, dict):
            raise InvalidMessageError("not_object", line_number)
        try:
            message = Message.model_validate(data)
        except ValidationError as exc:
            codes = [error_codes[error["type"]] for error in exc.errors(include_input=False)]
            raise InvalidMessageError(min(codes, key=priority.index), line_number) from None
        yield message


def read_jsonl(path: str | Path) -> Generator[Message, None, None]:
    """逐行读取 UTF-8 文件，迭代结束、发生异常或显式关闭时释放文件。"""
    with Path(path).open(encoding="utf-8") as stream:
        yield from parse_lines(stream)
