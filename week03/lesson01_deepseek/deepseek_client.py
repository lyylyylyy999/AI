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
        raise ValueError(f"{API_KEY_ENV_NAME}错误")
    if api_key is None or api_key.strip() == "":
        raise ValueError(f"{API_KEY_ENV_NAME} 不存在或者为空")
    return api_key


def bulid_deepseek_client(
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
    response = client.post("/chat/completions", json={"abstract": abstract})
    response.raise_for_status()
    return response.json()
