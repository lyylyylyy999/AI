"""W2-03 同步 HTTPX 客户端参考实现。"""

import httpx

SERVICE_BASE_URL = "https://research-api.example.test"
DEFAULT_TIMEOUT_SECONDS = 5.0


def build_client(
    transport: httpx.BaseTransport | None = None,
) -> httpx.Client:
    """构造带固定 base URL、Header 和 timeout 的同步客户端。"""
    return httpx.Client(
        base_url=SERVICE_BASE_URL,
        headers={"Accept": "application/json"},
        timeout=DEFAULT_TIMEOUT_SECONDS,
        transport=transport,
    )


def fetch_service_info(client: httpx.Client, language: str = "zh") -> object:
    """读取服务信息，并传播 HTTPX 原始异常。"""
    if not language.strip():
        raise ValueError("language: 不能为空")

    response = client.get("/v1/info", params={"lang": language})
    response.raise_for_status()
    result: object = response.json()
    return result


def submit_abstract(client: httpx.Client, abstract: str) -> object:
    """提交非空摘要，并返回尚未经过业务校验的 JSON 值。"""
    if not abstract.strip():
        raise ValueError("abstract: 不能为空")

    response = client.post("/v1/extract", json={"abstract": abstract})
    response.raise_for_status()
    result: object = response.json()
    return result
