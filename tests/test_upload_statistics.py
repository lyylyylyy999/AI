"""TASK-001 上传统计接口的合同测试，不修改生产实现。"""

import json
from collections.abc import Iterator
from typing import Any, BinaryIO, cast
from unittest.mock import Mock
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from httpx2 import Response
from starlette import formparsers

from app import main
from app.domain import Message
from app.jsonl import parse_lines

ENDPOINT = "/api/v1/logs/statistics"
MAX_BYTES = 2 * 1024 * 1024


def line(content: str = "正文", role: str = "user", conversation_id: str = "a") -> bytes:
    return (
        json.dumps(
            {"conversation_id": conversation_id, "role": role, "content": content},
            ensure_ascii=False,
        ).encode("utf-8")
        + b"\n"
    )


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    for key in ("DEEPSEEK_API_KEY", "DEEPSEEK_MODEL", "DATABASE_URL"):
        monkeypatch.delenv(key, raising=False)
    with TestClient(main.create_app()) as test_client:
        yield test_client


def upload(client: TestClient, payload: bytes) -> Response:
    return client.post(
        ENDPOINT, files={"file": ("日志.jsonl", payload, "application/octet-stream")}
    )


def request_id(response: Response) -> str:
    identifier = response.headers.get("X-Request-ID")
    assert isinstance(identifier, str), "响应应包含服务端请求ID"
    UUID(identifier)
    return identifier


def assert_error(response: Response, status: int, code: str) -> None:
    assert response.status_code == status
    body = response.json()
    assert body.get("code") == code, "错误码必须位于响应顶层"
    assert isinstance(body.get("message"), str) and body["message"].strip()
    assert body.get("request_id") == request_id(response)
    assert "Traceback" not in response.text


def test_sample_statistics_and_documentation(client: TestClient) -> None:
    response = upload(client, line("系统", "system") + line("你好") + line("收到", "assistant"))
    assert response.status_code == 200
    assert response.json() == {
        "total_messages": 3,
        "conversation_count": 1,
        "messages_by_role": {"system": 1, "user": 1, "assistant": 1},
        "total_characters": 6,
    }
    assert client.get("/health").json() == {"status": "ok"}
    request_id(client.get("/health"))
    assert client.get("/docs").status_code == 200
    assert ENDPOINT in client.get("/openapi.json").json()["paths"]


def test_multiple_conversations_zero_roles_and_original_whitespace(client: TestClient) -> None:
    response = upload(
        client, b"\n" + line(" 中文🙂 \n") + b" \t\n" + line("回答", conversation_id="b")
    )
    assert response.status_code == 200
    assert response.json() == {
        "total_messages": 2,
        "conversation_count": 2,
        "messages_by_role": {"system": 0, "user": 2, "assistant": 0},
        "total_characters": len(" 中文🙂 \n") + 2,
    }


def test_filename_and_content_type_are_not_used_for_validation(client: TestClient) -> None:
    response = client.post(
        ENDPOINT,
        files={"file": ("../不可信路径.exe", line(), "image/png")},
    )
    assert response.status_code == 200
    assert response.json()["total_messages"] == 1


def test_repeated_upload_is_stateless(client: TestClient) -> None:
    first, second = upload(client, line()), upload(client, line())
    assert first.status_code == second.status_code == 200
    assert first.json() == second.json()


def test_request_ids_are_new_and_do_not_trust_client_value(client: TestClient) -> None:
    spoofed = "00000000-0000-0000-0000-000000000000"
    first = client.post(
        ENDPOINT,
        files={"file": ("x.jsonl", line())},
        headers={"X-Request-ID": spoofed},
    )
    second = upload(client, line())
    assert first.status_code == second.status_code == 200
    assert request_id(first) != spoofed
    assert request_id(first) != request_id(second)


@pytest.mark.parametrize("wrong_field", [False, True])
def test_missing_or_nonfile_field_is_safe(client: TestClient, wrong_field: bool) -> None:
    response = client.post(ENDPOINT, data={"file": "secret-marker"} if wrong_field else {})
    assert response.status_code == 422
    assert "secret-marker" not in response.text, "框架校验错误不能回显输入"
    assert_error(response, 422, "invalid_request")


@pytest.mark.parametrize(
    ("payload", "code"),
    [
        (b"", "empty_log"),
        (b"\n \t\r\n", "empty_log"),
        (b"\xff", "invalid_encoding"),
    ],
)
def test_empty_or_invalid_encoding(client: TestClient, payload: bytes, code: str) -> None:
    assert_error(upload(client, payload), 422, code)


@pytest.mark.parametrize(
    ("record", "code"),
    [
        (b'{"secret-marker":', "invalid_json"),
        (b'["secret-marker"]', "not_object"),
        (b'{"content":"secret-marker"}', "missing_fields"),
        (b'{"conversation_id":"a","role":"user","content":"x","secret-marker":1}', "extra_fields"),
        (b'{"conversation_id":1,"role":"user","content":"secret-marker"}', "invalid_type"),
        (line("secret-marker", role="tool"), "invalid_role"),
        (line(" \t"), "blank_value"),
    ],
)
def test_late_invalid_record_has_line_number_without_partial_result(
    client: TestClient,
    record: bytes,
    code: str,
) -> None:
    response = upload(client, b"\n" + line() + record)
    assert response.status_code == 422
    assert "secret-marker" not in response.text
    assert_error(response, 422, code)
    assert response.json()["line_number"] == 3
    assert "total_messages" not in response.json()


def test_bom_is_not_silently_accepted(client: TestClient) -> None:
    assert_error(upload(client, b"\xef\xbb\xbf" + line()), 422, "invalid_json")


@pytest.mark.parametrize("separator", ["\u2028", "\u0085"])
def test_unicode_content_is_not_split_into_physical_lines(
    client: TestClient, separator: str
) -> None:
    content = "甲" + separator + "乙"
    response = upload(client, line(content))
    assert response.status_code == 200, "JSON字符串内的Unicode分隔字符不是JSONL换行"
    assert response.json()["total_characters"] == 3


@pytest.mark.parametrize("newline", [b"\n", b"\r\n", b"\r"])
def test_physical_newlines_preserve_error_line_number(client: TestClient, newline: bytes) -> None:
    response = upload(client, newline + line().rstrip(b"\n") + newline + b"invalid")
    assert_error(response, 422, "invalid_json")
    assert response.json()["line_number"] == 3


def test_file_at_exact_byte_limit_is_allowed(client: TestClient) -> None:
    # 用JSON尾部空格填充一个合法物理行，不增加消息数或正文长度。
    record = line()
    payload = record[:-1] + b" " * (MAX_BYTES - len(record)) + b"\n"
    assert len(payload) == MAX_BYTES
    response = upload(client, payload)
    assert response.status_code == 200
    assert response.json()["total_messages"] == 1


def test_oversized_file_is_rejected_before_decoding(client: TestClient) -> None:
    assert_error(upload(client, b"\xff" * (MAX_BYTES + 1)), 413, "file_too_large")


def test_exact_message_limit_is_allowed(client: TestClient) -> None:
    response = upload(client, line("字") * 10000)
    assert response.status_code == 200
    assert response.json()["total_messages"] == 10000
    assert response.json()["total_characters"] == 10000


def test_message_over_limit(client: TestClient) -> None:
    assert_error(upload(client, line("字") * 10001), 422, "too_many_messages")


@pytest.mark.parametrize(
    ("count", "expected_code"),
    [
        (9999, "invalid_json"),
        (10001, "too_many_messages"),
    ],
)
def test_error_priority_stops_when_limit_is_reached(
    client: TestClient,
    count: int,
    expected_code: str,
) -> None:
    assert_error(upload(client, line("字") * count + b"invalid"), 422, expected_code)


def test_parser_does_not_consume_beyond_message_limit(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    consumed = 0

    def observed(lines: Iterator[str]) -> Iterator[Message]:
        nonlocal consumed
        for message in parse_lines(lines):
            consumed += 1
            yield message

    monkeypatch.setattr(main, "parse_lines", observed)
    response = upload(client, line("字") * 10002)
    assert response.status_code == 422
    assert consumed == 10001, "只需读取第一条超限消息，不应继续无界消费"


@pytest.fixture
def observed_uploads(monkeypatch: pytest.MonkeyPatch) -> tuple[list[BinaryIO], list[int]]:
    """保留真实multipart解析，仅观察框架实际创建的上传文件。"""
    streams: list[BinaryIO] = []
    sizes: list[int] = []
    original_factory = getattr(formparsers, "SpooledTemporaryFile")

    def factory(*args: Any, **kwargs: Any) -> Any:
        stream = original_factory(*args, **kwargs)
        original_read = stream.read

        def read(size: int = -1) -> bytes:
            sizes.append(size)
            return cast(bytes, original_read(size))

        monkeypatch.setattr(stream, "read", read)
        streams.append(cast(BinaryIO, stream))
        return stream

    monkeypatch.setattr(formparsers, "SpooledTemporaryFile", factory)
    return streams, sizes


def test_uploaded_file_read_is_bounded(
    client: TestClient,
    observed_uploads: tuple[list[BinaryIO], list[int]],
) -> None:
    response = upload(client, line())
    streams, sizes = observed_uploads
    assert response.status_code == 200
    assert len(streams) == 1 and sizes, "必须观察到实际进入路由的上传文件读取"
    assert all(0 <= size <= MAX_BYTES + 1 for size in sizes), "禁止无界read()"


@pytest.mark.parametrize(
    ("payload", "status"),
    [
        (line(), 200),
        (b"invalid", 422),
        (b"\xff", 422),
        (b"", 422),
        (b"x" * (MAX_BYTES + 1), 413),
    ],
    ids=["success", "invalid-json", "invalid-encoding", "empty", "oversized"],
)
def test_upload_resources_close_on_success_and_expected_failure(
    client: TestClient,
    observed_uploads: tuple[list[BinaryIO], list[int]],
    payload: bytes,
    status: int,
) -> None:
    response = upload(client, payload)
    streams, _ = observed_uploads
    assert response.status_code == status
    assert len(streams) == 1, "关闭断言必须观察到真实上传对象"
    assert streams[0].closed


def test_unexpected_failure_stays_server_error_and_closes_upload(
    observed_uploads: tuple[list[BinaryIO], list[int]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    failure = Mock(side_effect=RuntimeError("合成内部错误"))
    monkeypatch.setattr(main, "summarize", failure)
    with TestClient(main.create_app(), raise_server_exceptions=False) as client:
        response = upload(client, line())
    streams, _ = observed_uploads
    failure.assert_called_once()
    assert_error(response, 500, "internal_error")
    assert len(streams) == 1 and streams[0].closed
    assert "合成内部错误" not in response.text
