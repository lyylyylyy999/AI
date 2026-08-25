import httpx
import pytest
from deepseek_client import (
    bulid_deepseek_client,
    get_api_key,
    request_research_extraction,
)


def test_fake_key() -> None:
    env = {"DEEPSEEK_API_KEY": "123456"}
    api_key = get_api_key(env)
    assert api_key == "123456"


@pytest.mark.parametrize(
    ("env", "exception", "match"),
    [
        ({"DEEPSEEK_API_KEY": None}, ValueError, "DEEPSEEK_API_KEY 不存在或者为空"),
        ({"DEEPSEEK_API_KEY": "  "}, ValueError, "DEEPSEEK_API_KEY 不存在或者为空"),
        ({"DEEPSEEK_API_KEY": "\t"}, ValueError, "DEEPSEEK_API_KEY 不存在或者为空"),
    ],
    ids=("key_none", "key_empty", "key_blank"),
)
def test_invalid_key(
    env: dict[str, str], exception: type[Exception], match: str
) -> None:
    with pytest.raises(exception, match=match):
        get_api_key(env)


def test_request_research_extraction() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.host == "api.deepseek.com"
        assert request.url.path == "/chat/completions"
        assert request.headers["Accept"] == "application/json"
        assert request.headers["Authorization"] == "Bearer 123456"
        return httpx.Response(
            200,
            json={
                "model": "deepseek-v4-flash",
                "messages": [
                    {"role": "system", "content": "..."},
                    {"role": "user", "content": "用户摘要"},
                ],
                "response_format": {"type": "json_object"},
                "thinking": {"type": "disabled"},
                "stream": False,
                "max_tokens": 1024,
            },
        )

    transport = httpx.MockTransport(handler)
    env = {"DEEPSEEK_API_KEY": "123456"}
    api_key = get_api_key(env)
    with bulid_deepseek_client(api_key, transport) as client:
        result = request_research_extraction(client, "123")
        assert result == {
            "model": "deepseek-v4-flash",
            "messages": [
                {"role": "system", "content": "..."},
                {"role": "user", "content": "用户摘要"},
            ],
            "response_format": {"type": "json_object"},
            "thinking": {"type": "disabled"},
            "stream": False,
            "max_tokens": 1024,
        }


def test_timeout() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        timeout = request.extensions.get("timeout")
        assert timeout is not None
        assert timeout["connect"] == 30.0
        assert timeout["read"] == 30.0
        assert timeout["write"] == 30.0
        assert timeout["pool"] == 30.0
        return httpx.Response(
            200,
            json={
                "model": "deepseek-v4-flash",
                "messages": [
                    {"role": "system", "content": "..."},
                    {"role": "user", "content": "用户摘要"},
                ],
                "response_format": {"type": "json_object"},
                "thinking": {"type": "disabled"},
                "stream": False,
                "max_tokens": 1024,
            },
        )

    transport = httpx.MockTransport(handler)
    env = {"DEEPSEEK_API_KEY": "123456"}
    api_key = get_api_key(env)
    with bulid_deepseek_client(api_key, transport) as client:
        request_research_extraction(client, "1234")


def test_empty_abstract() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "model": "deepseek-v4-flash",
                "messages": [
                    {"role": "system", "content": "..."},
                    {"role": "user", "content": "用户摘要"},
                ],
                "response_format": {"type": "json_object"},
                "thinking": {"type": "disabled"},
                "stream": False,
                "max_tokens": 1024,
            },
        )

    transport = httpx.MockTransport(handler)
    env = {"DEEPSEEK_API_KEY": "123456"}
    api_key = get_api_key(env)
    with (
        pytest.raises(ValueError, match="摘要不能为空"),
        bulid_deepseek_client(api_key, transport) as client,
    ):
        request_research_extraction(client, " ")


def test_httpstatuserror_with_401() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401)

    transport = httpx.MockTransport(handler)
    env = {"DEEPSEEK_API_KEY": "123456"}
    api_key = get_api_key(env)
    with (
        bulid_deepseek_client(api_key, transport) as client,
        pytest.raises(httpx.HTTPStatusError) as exc_info,
    ):
        request_research_extraction(client, "1234")
    assert exc_info.value.response.status_code == 401


def test_handler_with_exception() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("超时", request=request)

    transport = httpx.MockTransport(handler)
    env = {"DEEPSEEK_API_KEY": "123456"}
    api_key = get_api_key(env)
    with (
        pytest.raises(httpx.ReadTimeout, match="超时"),
        bulid_deepseek_client(api_key, transport) as client,
    ):
        request_research_extraction(client, "1234")


if __name__ == "__main__":
    pytest.main(["week03/lesson01_deepseek/test_deepseek_client.py", "-qs"])
