"""W3-01 DeepSeek V4 最小同步客户端参考实现。"""

from collections.abc import Mapping

import httpx

DEEPSEEK_BASE_URL = "https://api.deepseek.com"
CHAT_COMPLETIONS_PATH = "/chat/completions"
DEEPSEEK_MODEL = "deepseek-v4-flash"
DEFAULT_TIMEOUT_SECONDS = 30.0
API_KEY_ENV_NAME = "DEEPSEEK_API_KEY"

SYSTEM_PROMPT = """你是一名研究摘要信息提取助手。
只返回合法的 JSON 对象，并且只能包含以下六个字段：
- research_question：字符串
- data_source：字符串
- sample_size：正整数；未报告时使用 null
- statistical_methods：字符串数组；未报告时使用空数组
- key_findings：字符串数组；未报告时使用空数组
- limitations：字符串数组；未报告时使用空数组
不要返回 JSON 之外的解释文字。"""


def get_api_key(environ: Mapping[str, str]) -> str:
    """从显式注入的环境变量 mapping 中读取非空 API Key。"""
    try:
        api_key = environ[API_KEY_ENV_NAME]
    except KeyError:
        raise ValueError(f"{API_KEY_ENV_NAME}: 不存在") from None

    if not api_key.strip():
        raise ValueError(f"{API_KEY_ENV_NAME}: 不能为空")
    return api_key


def build_deepseek_client(
    api_key: str,
    transport: httpx.BaseTransport | None = None,
) -> httpx.Client:
    """构造带认证、固定 base URL 和显式 timeout 的同步客户端。"""
    return httpx.Client(
        base_url=DEEPSEEK_BASE_URL,
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        timeout=DEFAULT_TIMEOUT_SECONDS,
        transport=transport,
    )


def request_research_extraction(
    client: httpx.Client,
    abstract: str,
) -> object:
    """提交非空研究摘要，并返回尚未解析 choices 的响应 JSON 值。"""
    if not abstract.strip():
        raise ValueError("abstract: 不能为空")

    response = client.post(
        CHAT_COMPLETIONS_PATH,
        json={
            "model": DEEPSEEK_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": abstract},
            ],
            "response_format": {"type": "json_object"},
            "thinking": {"type": "disabled"},
            "stream": False,
            "max_tokens": 1024,
        },
    )
    response.raise_for_status()
    result: object = response.json()
    return result
