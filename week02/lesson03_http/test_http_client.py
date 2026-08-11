import json

import httpx
import pytest
from http_client import build_client, fetch_service_info, submit_abstract


def test_get() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.host == "research-api.example.test"
        assert request.url.path == "/v1/info"
        assert request.headers["Accept"] == "application/json"
        return httpx.Response(200, json={"status": "ok"})

    transport = httpx.MockTransport(handler)
    with build_client(transport) as client:
        result = fetch_service_info(client)
        assert result == {"status": "ok"}


def test_post() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/extract"
        body = json.loads(request.content)
        assert body == {"abstract": "1234"}
        return httpx.Response(200, json={"status": "ok"})

    transport = httpx.MockTransport(handler)
    with build_client(transport) as client:
        result = submit_abstract(client, "1234")
        assert result == {"status": "ok"}


def test_timeout() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.host == "research-api.example.test"
        assert request.url.path == "/v1/info"
        assert request.headers["Accept"] == "application/json"
        return httpx.Response(200, json={"status": "ok"})

    transport = httpx.MockTransport(handler)
    with build_client(transport) as client:
        assert client.timeout is not None


def test_abstract_is_empty() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/extract"
        body = json.loads(request.content)
        assert body == {"abstract": "1234"}
        return httpx.Response(200, json={"status": "ok"})

    transport = httpx.MockTransport(handler)
    with pytest.raises(ValueError), build_client(transport) as client:
        submit_abstract(client, "   ")


def test_httpstatuserror_with_404() -> None:
    def handler(reuqest: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"status": "fail"})

    transport = httpx.MockTransport(handler)
    with pytest.raises(httpx.HTTPStatusError), build_client(transport) as client:
        fetch_service_info(client)


def test_httpstatuserror_with_500() -> None:
    def handler(reuqest: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"status": "fail"})

    transport = httpx.MockTransport(handler)
    with pytest.raises(httpx.HTTPStatusError), build_client(transport) as client:
        fetch_service_info(client)


def test_handler_with_exception() -> None:
    def handler(reuqest: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("超时")

    transport = httpx.MockTransport(handler)
    with (
        pytest.raises(httpx.ReadTimeout, match="超时"),
        build_client(transport) as client,
    ):
        fetch_service_info(client)


def test_validate_arrray() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=["a", "b", "c"])

    transport = httpx.MockTransport(handler)
    with build_client(transport) as client:
        result = fetch_service_info(client)
        assert result == ["a", "b", "c"]


if __name__ == "__main__":
    pytest.main(["week02/lesson03_http/test_http_client.py", "-qs"])
