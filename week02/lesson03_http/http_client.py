import httpx

SERVICE_BASE_URL = "https://research-api.example.test"
DEFAULT_TIMEOUT_SECONDS = 5.0


def build_client(
    transport: httpx.BaseTransport | None = None,
) -> httpx.Client:
    client = httpx.Client(
        base_url=SERVICE_BASE_URL,
        transport=transport,
        timeout=DEFAULT_TIMEOUT_SECONDS,
        headers={"Accept": "application/json"},
    )
    return client


def fetch_service_info(client: httpx.Client, language: str = "zh") -> object:
    if language.strip() == "":
        raise ValueError("language 不能为空")
    response = client.get("/v1/info", params={"lang": language})
    response.raise_for_status()
    return response.json()


def submit_abstract(client: httpx.Client, abstract: str) -> object:
    if abstract.strip() == "":
        raise ValueError("abstract 不能为空")
    response = client.post("/v1/extract", json={"abstract": abstract})
    response.raise_for_status()
    return response.json()
