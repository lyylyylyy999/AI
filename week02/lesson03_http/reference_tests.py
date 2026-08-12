"""W2-03 同步 HTTPX 客户端参考测试。"""

import json
from collections.abc import Callable

import httpx
import pytest
from reference_solution import build_client, fetch_service_info, submit_abstract

Handler = Callable[[httpx.Request], httpx.Response]


def make_mock_client(handler: Handler) -> httpx.Client:
    return build_client(httpx.MockTransport(handler))


def test_get_request_contract_and_json_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.host == "research-api.example.test"
        assert request.url.path == "/v1/info"
        assert request.url.params["lang"] == "zh"
        assert request.headers["Accept"] == "application/json"
        return httpx.Response(200, json={"status": "ok"})

    with make_mock_client(handler) as client:
        assert fetch_service_info(client) == {"status": "ok"}


def test_post_request_contract_and_json_body() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/v1/extract"
        assert request.headers["Content-Type"] == "application/json"
        assert json.loads(request.content) == {"abstract": "研究摘要"}
        return httpx.Response(200, json={"accepted": True})

    with make_mock_client(handler) as client:
        assert submit_abstract(client, "研究摘要") == {"accepted": True}


def test_request_has_explicit_five_second_timeout() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.extensions["timeout"] == {
            "connect": 5.0,
            "read": 5.0,
            "write": 5.0,
            "pool": 5.0,
        }
        return httpx.Response(200, json={})

    with make_mock_client(handler) as client:
        fetch_service_info(client)


def test_blank_abstract_fails_before_transport_is_called() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError(f"不应发送请求: {request.url}")

    with (
        make_mock_client(handler) as client,
        pytest.raises(ValueError, match="abstract"),
    ):
        submit_abstract(client, "   ")


@pytest.mark.parametrize("status_code", [404, 500])
def test_http_status_error_preserves_response(status_code: int) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, request=request, json={"error": "failed"})

    with (
        make_mock_client(handler) as client,
        pytest.raises(httpx.HTTPStatusError) as exc_info,
    ):
        fetch_service_info(client)

    assert exc_info.value.response.status_code == status_code


def test_read_timeout_preserves_request() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("读取超时", request=request)

    with (
        make_mock_client(handler) as client,
        pytest.raises(httpx.ReadTimeout, match="读取超时") as exc_info,
    ):
        fetch_service_info(client)

    assert exc_info.value.request.url.path == "/v1/info"


def test_http_layer_can_return_json_array() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, request=request, json=["a", "b"])

    with make_mock_client(handler) as client:
        assert fetch_service_info(client) == ["a", "b"]


def test_get_request_accepts_custom_language() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["lang"] == "en"
        return httpx.Response(200, json={"status": "ok"})

    with make_mock_client(handler) as client:
        fetch_service_info(client, language="en")


def test_blank_language_fails_before_transport_is_called() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError(f"不应发送请求: {request.url}")

    with (
        make_mock_client(handler) as client,
        pytest.raises(ValueError, match="language"),
    ):
        fetch_service_info(client, language="   ")
