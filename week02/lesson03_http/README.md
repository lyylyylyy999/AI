# W2-03：同步 HTTP 与 HTTPX MockTransport

预计用时：60–90 分钟。本任务不调用 DeepSeek，不读取 API Key，自动化测试不得访问真实网络。

## 目标

完成后你应当能够：

1. 解释 URL、请求方法、Header、Body、状态码和响应之间的关系。
2. 使用同步 `httpx.Client` 发送 GET 与 JSON POST 请求。
3. 在生产客户端中显式设置 timeout。
4. 使用 `response.raise_for_status()` 区分成功响应与 4xx/5xx。
5. 区分 HTTP 状态错误、超时和其他网络请求错误。
6. 使用 `httpx.MockTransport` 测试请求，而不访问网络。

## 已确认的工具版本

本项目使用稳定版 `httpx==0.28.1`，记录在仓库根目录 `requirements.txt`。HTTPX 1.0 当前只有开发预发布版，本阶段不使用预发布依赖。

官方资料：

- [HTTPX QuickStart](https://www.python-httpx.org/quickstart/)
- [HTTPX Exceptions](https://www.python-httpx.org/exceptions/)
- [HTTPX Timeouts](https://www.python-httpx.org/advanced/timeouts/)
- [HTTPX Mock transports](https://www.python-httpx.org/advanced/transports/#mock-transports)

## HTTP 数据流

```text
客户端
  └─ Request
       ├─ URL：请求发往哪里
       ├─ Method：GET、POST 等操作语义
       ├─ Headers：内容类型、认证、客户端信息等元数据
       └─ Body：POST 等请求携带的数据
            ↓
          服务器
            ↓
  ┌─ Response
  │    ├─ Status code：处理结果类别
  │    ├─ Headers：响应元数据
  │    └─ Body：文本、JSON、文件等响应内容
  └─ 客户端解析与业务校验
```

### URL

以 `https://research-api.example.test/v1/info?lang=zh` 为例：

- `https`：scheme，通信协议。
- `research-api.example.test`：host，目标主机。
- `/v1/info`：path，资源路径。
- `lang=zh`：query parameter，请求参数。

`.test` 是为测试保留的域名。本练习所有请求都必须由 MockTransport 截获。

### GET 与 POST

- GET 通常用于读取资源，请求参数常放在 URL query 中。
- POST 通常用于提交或创建数据，请求数据可放在 body 中。
- `client.post(..., json=payload)` 会把 Python 对象序列化为 JSON body，并设置相应 Content-Type。

“GET 一定没有 body”不是绝对协议禁令，但常规 API 设计中不要依赖 GET body。

### 状态码与异常

收到 HTTP 响应不等于请求成功：404、429、500 都已经收到服务器响应。只有调用 `response.raise_for_status()`，HTTPX 才会把非成功状态转换为 `httpx.HTTPStatusError`。

超时、DNS、连接中断等发生在请求或传输阶段，属于 `httpx.RequestError` 分支；timeout 更具体地属于 `httpx.TimeoutException`。它们与 HTTPStatusError 的核心区别是：前者通常没有可用的业务 HTTP 响应。

## 本次接口契约

在 `week02/lesson03_http/http_client.py` 中定义：

```python
SERVICE_BASE_URL = "https://research-api.example.test"
DEFAULT_TIMEOUT_SECONDS = 5.0


def build_client(
    transport: httpx.BaseTransport | None = None,
) -> httpx.Client:
    ...


def fetch_service_info(client: httpx.Client) -> object:
    ...


def submit_abstract(client: httpx.Client, abstract: str) -> object:
    ...
```

### `build_client`


- 使用 `SERVICE_BASE_URL` 作为 `base_url`。
- 显式设置 5 秒 timeout，不能使用 `None`。
- 默认 Header 至少包含 `Accept: application/json`。
- 接收可选 transport，使测试可以注入 `httpx.MockTransport`。
- 不发送请求，只负责构造并返回同步客户端。

### `fetch_service_info`

- GET `/v1/info`。
- 调用 `raise_for_status()`。
- 返回 `response.json()` 解析出的 Python 对象。
- 返回类型暂时是 `object`：HTTP 层不假定响应满足业务契约。

### `submit_abstract`

- 若 `abstract` 去除首尾空白后为空，先抛出 `ValueError`，不能发送请求。
- POST `/v1/extract`。
- JSON body 为 `{"abstract": 原始文本}`。
- 调用 `raise_for_status()`。
- 返回 JSON 解析出的 Python `object`。

本阶段让 HTTPX 原始异常继续向上传播，不在这里翻译为自定义错误。错误翻译会在后续 API 客户端阶段处理。

## MockTransport 最小示例

以下只演示 MockTransport 的形状，不是任务答案：

```python
import httpx


def handler(request: httpx.Request) -> httpx.Response:
    assert request.method == "GET"
    return httpx.Response(200, json={"status": "ok"})


transport = httpx.MockTransport(handler)
```

handler 收到真实构造出的 `httpx.Request`，因此测试可以检查 method、URL、headers 和 body；返回值则模拟服务器响应。

## 测试要求

在 `week02/lesson03_http/test_http_client.py` 中至少覆盖：

1. GET 使用正确 method、host、path 和 Accept Header，并返回解析后的 JSON。
2. POST 使用正确 path 和 JSON body；测试通过解析 `request.content` 验证 body，不比较手写 JSON 字符串。
3. 请求扩展中的 timeout 已设置，且不是 `None`。
4. 空摘要在发送前抛出 `ValueError`；handler 不应被调用。
5. Mock 返回 404 或 500 时，函数抛出 `httpx.HTTPStatusError`，并能从异常响应读取状态码。
6. handler 主动抛出 `httpx.ReadTimeout` 时，函数传播该异常。
7. 服务返回合法 JSON 数组时，函数可返回 `list`，证明 HTTP 层没有冒充业务校验层。

每个测试通过 `build_client(transport)` 注入 MockTransport，并使用 `with` 关闭客户端。

## 验收标准

- 测试期间没有真实 DNS 或网络访问。
- 生产代码使用同步 API，没有 `async` / `await`。
- timeout 显式配置且不是 `None`。
- GET、POST、Header 和 JSON Body 均由测试直接验证。
- 非 2xx 必须通过 `raise_for_status()` 转为 `HTTPStatusError`。
- 未捕获或泄漏 Authorization Header；本任务不需要认证头。
- 返回类型诚实地使用 `object`，没有 `Any`、`cast()` 或 `# type: ignore`。
- Ruff、mypy strict 和 pytest 全部通过。

## 运行命令

```powershell
.\.venv\Scripts\python.exe -c "import httpx; print(httpx.__version__)"
.\.venv\Scripts\ruff.exe check week02\lesson03_http
.\.venv\Scripts\ruff.exe format --check week02\lesson03_http
.\.venv\Scripts\mypy.exe --strict week02\lesson03_http\http_client.py week02\lesson03_http\test_http_client.py
.\.venv\Scripts\python.exe -m pytest week02\lesson03_http\test_http_client.py -q
```

## 完成后回复

```text
W2-03 完成
用时：
测试数：
HTTPX 版本：
Ruff：
mypy：
pytest：
HTTPStatusError 与 RequestError 的区别：
为什么 HTTP 层返回 object：
```
