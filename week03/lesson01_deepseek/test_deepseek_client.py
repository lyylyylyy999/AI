import json

import httpx
import pytest
from deepseek_client import (
    build_deepseek_client,
    get_api_key,
    request_research_extraction,
)


def test_fake_key() -> None:
    env = {"DEEPSEEK_API_KEY": "test-key-not-secret"}
    api_key = get_api_key(env)
    assert api_key == "test-key-not-secret"


@pytest.mark.parametrize(
    ("env", "exception", "match"),
    [
        ({}, ValueError, "DEEPSEEK_API_KEY 不存在"),
        ({"DEEPSEEK_API_KEY": ""}, ValueError, "DEEPSEEK_API_KEY 为空"),
        ({"DEEPSEEK_API_KEY": "  "}, ValueError, "DEEPSEEK_API_KEY 为空"),
    ],
    ids=("missing", "empty", "blank"),
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
        assert request.headers["Authorization"] == "Bearer test-key-not-secret"
        body = json.loads(request.content)
        assert body == {
            "model": "deepseek-v4-flash",
            "messages": [
                {
                    "role": "system",
                    "content": "你是一名专业的数据提取专家，你的任务是根据用户的输入摘要，提取指定的业务信息。\n\n你必须遵循以下规则：\n1. 只返回合法的 JSON 对象；\n2. 你的返回结果只能包含以下 6 个字段：\n- research_question(字符串);\n- data_source(字符串);\n- sample_size(字符串),sample_size 未报告时使用 null;\n- statistical_methods(字符串数组);\n- key_findings(字符串数组);\n- limitations(字符串数组);\n3. statistical_methods、key_findings、limitations 未报告时使用空数组",
                },
                {"role": "user", "content": "123"},
            ],
            "response_format": {"type": "json_object"},
            "thinking": {"type": "disabled"},
            "stream": False,
            "max_tokens": 1024,
        }
        return httpx.Response(200, json={"accepted": True})

    transport = httpx.MockTransport(handler)
    env = {"DEEPSEEK_API_KEY": "test-key-not-secret"}
    api_key = get_api_key(env)
    with build_deepseek_client(api_key, transport) as client:
        result = request_research_extraction(client, "123")
        assert result == {"accepted": True}


def test_timeout() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        timeout = request.extensions.get("timeout")
        assert timeout is not None
        assert timeout["connect"] == 30.0
        assert timeout["read"] == 30.0
        assert timeout["write"] == 30.0
        assert timeout["pool"] == 30.0
        return httpx.Response(200, json={"accepted": True})

    transport = httpx.MockTransport(handler)
    env = {"DEEPSEEK_API_KEY": "test-key-not-secret"}
    api_key = get_api_key(env)
    with build_deepseek_client(api_key, transport) as client:
        request_research_extraction(client, "1234")


def test_empty_abstract() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError(f"不应发送请求: {request.url}")

    transport = httpx.MockTransport(handler)
    env = {"DEEPSEEK_API_KEY": "test-key-not-secret"}
    api_key = get_api_key(env)
    with (
        pytest.raises(ValueError, match="摘要不能为空"),
        build_deepseek_client(api_key, transport) as client,
    ):
        request_research_extraction(client, " ")


def test_httpstatuserror_with_401() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401)

    transport = httpx.MockTransport(handler)
    env = {"DEEPSEEK_API_KEY": "test-key-not-secret"}
    api_key = get_api_key(env)
    with (
        build_deepseek_client(api_key, transport) as client,
        pytest.raises(httpx.HTTPStatusError) as exc_info,
    ):
        request_research_extraction(client, "1234")
    assert exc_info.value.response.status_code == 401


def test_handler_with_exception() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("超时", request=request)

    transport = httpx.MockTransport(handler)
    env = {"DEEPSEEK_API_KEY": "test-key-not-secret"}
    api_key = get_api_key(env)
    with (
        pytest.raises(httpx.ReadTimeout, match="超时") as exc_info,
        build_deepseek_client(api_key, transport) as client,
    ):
        request_research_extraction(client, "1234")
    assert exc_info.value.request.url.path == "/chat/completions"


if __name__ == "__main__":
    pytest.main(["week03/lesson01_deepseek/test_deepseek_client.py", "-qs"])
