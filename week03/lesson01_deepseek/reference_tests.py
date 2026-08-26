"""W3-01 DeepSeek V4 最小同步客户端参考测试。"""

import json

import httpx
import pytest
from reference_solution import (
    API_KEY_ENV_NAME,
    build_deepseek_client,
    get_api_key,
    request_research_extraction,
)

FAKE_KEY = "test-key-not-secret"


def test_get_api_key_reads_injected_mapping() -> None:
    assert get_api_key({API_KEY_ENV_NAME: FAKE_KEY}) == FAKE_KEY


@pytest.mark.parametrize(
    "environ",
    [{}, {API_KEY_ENV_NAME: ""}, {API_KEY_ENV_NAME: "   "}],
    ids=["missing", "empty", "blank"],
)
def test_get_api_key_rejects_missing_or_blank_value(
    environ: dict[str, str],
) -> None:
    with pytest.raises(ValueError, match=API_KEY_ENV_NAME) as exc_info:
        get_api_key(environ)

    assert FAKE_KEY not in str(exc_info.value)


def test_request_contract_and_success_response_are_separate() -> None:
    abstract = "研究摘要"
    response_data = {
        "choices": [{"message": {"content": '{"research_question": "问题"}'}}]
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.host == "api.deepseek.com"
        assert request.url.path == "/chat/completions"
        assert request.headers["Accept"] == "application/json"
        assert request.headers["Authorization"] == f"Bearer {FAKE_KEY}"
        assert request.headers["Content-Type"] == "application/json"

        body = json.loads(request.content)
        assert body["model"] == "deepseek-v4-flash"
        assert body["messages"][0]["role"] == "system"
        system_prompt = body["messages"][0]["content"]
        assert "JSON" in system_prompt
        for field in (
            "research_question",
            "data_source",
            "sample_size",
            "statistical_methods",
            "key_findings",
            "limitations",
        ):
            assert field in system_prompt
        assert "正整数" in system_prompt
        assert "null" in system_prompt
        assert "空数组" in system_prompt
        assert body["messages"][1] == {"role": "user", "content": abstract}
        assert body["response_format"] == {"type": "json_object"}
        assert body["thinking"] == {"type": "disabled"}
        assert body["stream"] is False
        assert body["max_tokens"] == 1024
        return httpx.Response(200, request=request, json=response_data)

    transport = httpx.MockTransport(handler)
    with build_deepseek_client(FAKE_KEY, transport) as client:
        result = request_research_extraction(client, abstract)

    assert result == response_data


def test_request_has_explicit_thirty_second_timeout() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.extensions["timeout"] == {
            "connect": 30.0,
            "read": 30.0,
            "write": 30.0,
            "pool": 30.0,
        }
        return httpx.Response(200, request=request, json={})

    transport = httpx.MockTransport(handler)
    with build_deepseek_client(FAKE_KEY, transport) as client:
        request_research_extraction(client, "研究摘要")


def test_blank_abstract_fails_before_transport_is_called() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError(f"不应发送请求: {request.url}")

    transport = httpx.MockTransport(handler)
    with (
        build_deepseek_client(FAKE_KEY, transport) as client,
        pytest.raises(ValueError, match="abstract"),
    ):
        request_research_extraction(client, "   ")


def test_401_response_raises_http_status_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, request=request, json={"error": "unauthorized"})

    transport = httpx.MockTransport(handler)
    with (
        build_deepseek_client(FAKE_KEY, transport) as client,
        pytest.raises(httpx.HTTPStatusError) as exc_info,
    ):
        request_research_extraction(client, "研究摘要")

    assert exc_info.value.response.status_code == 401


def test_read_timeout_is_propagated_with_request() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("读取超时", request=request)

    transport = httpx.MockTransport(handler)
    with (
        build_deepseek_client(FAKE_KEY, transport) as client,
        pytest.raises(httpx.ReadTimeout, match="读取超时") as exc_info,
    ):
        request_research_extraction(client, "研究摘要")

    assert exc_info.value.request.url.path == "/chat/completions"
