from collections.abc import Mapping

import httpx

DEEPSEEK_BASE_URL = "https://api.deepseek.com"
CHAT_COMPLETIONS_PATH = "/chat/completions"
DEEPSEEK_MODEL = "deepseek-v4-flash"
DEFAULT_TIMEOUT_SECONDS = 30.0
API_KEY_ENV_NAME = "DEEPSEEK_API_KEY"


def get_api_key(environ: Mapping[str, str]) -> str:
    try:
        api_key = environ[API_KEY_ENV_NAME]
    except KeyError:
        raise ValueError(f"{API_KEY_ENV_NAME} 不存在")
    if api_key.strip() == "":
        raise ValueError(f"{API_KEY_ENV_NAME} 为空")
    return api_key


def build_deepseek_client(
    api_key: str,
    transport: httpx.BaseTransport | None = None,
) -> httpx.Client:
    deepseek_client = httpx.Client(
        base_url=DEEPSEEK_BASE_URL,
        transport=transport,
        timeout=DEFAULT_TIMEOUT_SECONDS,
        headers={"Accept": "application/json", "Authorization": f"Bearer {api_key}"},
    )
    return deepseek_client


def request_research_extraction(
    client: httpx.Client,
    abstract: str,
) -> object:
    if abstract.strip() == "":
        raise ValueError("摘要不能为空")
    response = client.post(
        CHAT_COMPLETIONS_PATH,
        json={
            "model": DEEPSEEK_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一名专业的数据提取专家，你的任务是根据用户的输入摘要，提取指定的业务信息。\n\n你必须遵循以下规则：\n1. 只返回合法的 JSON 对象；\n2. 你的返回结果只能包含以下 6 个字段：\n- research_question(字符串);\n- data_source(字符串);\n- sample_size(正整数或 null),sample_size 未报告时使用 null;\n- statistical_methods(字符串数组);\n- key_findings(字符串数组);\n- limitations(字符串数组);\n3. statistical_methods、key_findings、limitations 未报告时使用空数组",
                },
                {"role": "user", "content": abstract},
            ],
            "response_format": {"type": "json_object"},
            "thinking": {"type": "disabled"},
            "stream": False,
            "max_tokens": 1024,
        },
    )
    response.raise_for_status()
    return response.json()
