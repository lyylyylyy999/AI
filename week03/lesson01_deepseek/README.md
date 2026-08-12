# W3-01：DeepSeek V4 最小同步客户端

预计用时：60–90 分钟。本任务只使用 MockTransport，不发起真实 DeepSeek 请求，不读取真实 `.env` 或 API Key。

## 官方文档核对结果

核对日期：2026-08-11。

| 项目 | 当前官方契约 |
|---|---|
| Base URL | `https://api.deepseek.com` |
| Chat endpoint | `POST /chat/completions` |
| 认证 | `Authorization: Bearer <API_KEY>` |
| 当前模型 | `deepseek-v4-flash`、`deepseek-v4-pro` |
| 本项目模型 | `deepseek-v4-flash` |
| JSON Output | `response_format={"type": "json_object"}` |
| 非流式 | `stream=false` |
| 本项目思考模式 | `thinking={"type": "disabled"}` |

官方更新说明：旧模型名 `deepseek-chat` 和 `deepseek-reasoner` 已在 2026-07-24 到达停用节点。不要复制仍使用旧模型名的教程。

官方资料：

- [Create Chat Completion](https://api-docs.deepseek.com/api/create-chat-completion)
- [Models & Pricing](https://api-docs.deepseek.com/quick_start/pricing)
- [JSON Output](https://api-docs.deepseek.com/guides/json_mode/)
- [Authentication](https://api-docs.deepseek.com/api/deepseek-api)
- [Error Codes](https://api-docs.deepseek.com/quick_start/error_codes/)

## 本课目标

完成后你应当能够：

1. 从环境变量边界读取 API Key，并对缺失或空值给出明确错误。
2. 构造不会把密钥写入源码的 Bearer Authorization Header。
3. 使用 HTTPX 发送符合当前 DeepSeek V4 契约的 JSON 请求。
4. 在测试中检查请求，但不打印或泄漏 Authorization Header。
5. 保持“HTTP 响应 JSON”与“模型生成文本”分离。

## 三层数据尚未合并

```text
HTTP response JSON
  └─ choices[0].message.content（模型文本，仍是 str）
       └─ json.loads(content)（业务候选数据）
            └─ validate_research_summary（已验证业务数据）
```

W3-01 只完成第一层：构造请求并返回 HTTP response JSON 对应的 Python `object`。不要在本任务中解析 `choices` 或模型生成的 JSON 字符串，那是 W3-02。

## 安全规则

- 只使用环境变量名 `DEEPSEEK_API_KEY`。
- 自动化测试使用明显的假 Key，例如 `test-key-not-secret`。
- 不读取或打印 `.env`。
- 不在异常消息、日志、断言失败消息中输出完整 Authorization Header。
- 不把真实 Key 作为函数默认值或常量。
- 不在测试中读取真实 `os.environ`。

## 独立任务

在 `week03/lesson01_deepseek/` 下创建：

- `deepseek_client.py`
- `test_deepseek_client.py`

### 1. 常量

定义：

```python
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
CHAT_COMPLETIONS_PATH = "/chat/completions"
DEEPSEEK_MODEL = "deepseek-v4-flash"
DEFAULT_TIMEOUT_SECONDS = 30.0
API_KEY_ENV_NAME = "DEEPSEEK_API_KEY"
```

大模型生成响应通常比普通 HTTP API 慢，本阶段客户端使用显式 30 秒 timeout。真实调用时是否需要调整，要以后根据测量结果决定。

### 2. 环境变量边界

实现：

```python
from collections.abc import Mapping


def get_api_key(environ: Mapping[str, str]) -> str:
    ...
```

- 只从传入的 mapping 读取 `DEEPSEEK_API_KEY`。
- 缺少、空字符串或纯空白时抛出 `ValueError`。
- 错误消息可以包含环境变量名，但不能包含任何 Key 值。
- 返回值保留原始 Key，不要自行截断或改写。

为什么这次不让函数内部直接读取 `os.environ`：显式依赖更容易测试，也保证自动化测试不会意外碰到真实环境。未来 CLI 入口可以调用 `get_api_key(os.environ)`。

### 3. 构造客户端

实现：

```python
def build_deepseek_client(
    api_key: str,
    transport: httpx.BaseTransport | None = None,
) -> httpx.Client:
    ...
```

- `base_url` 使用官方地址。
- timeout 为 30 秒。
- 默认 Header：
  - `Accept: application/json`
  - `Authorization: Bearer <api_key>`
- transport 参数用于注入 MockTransport。
- 函数只构造客户端，不发送请求。

### 4. 构造研究摘要请求

实现：

```python
def request_research_extraction(
    client: httpx.Client,
    abstract: str,
) -> object:
    ...
```

- 摘要为空或纯空白时，在发送请求前抛出 `ValueError`。
- POST `/chat/completions`。
- 调用 `raise_for_status()`。
- 返回 `response.json()` 对应的 Python `object`，不解析 `choices`。

请求 JSON body 至少包含：

```json
{
  "model": "deepseek-v4-flash",
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "用户摘要"}
  ],
  "response_format": {"type": "json_object"},
  "thinking": {"type": "disabled"},
  "stream": false,
  "max_tokens": 1024
}
```

System prompt 必须：

- 明确要求只返回 JSON。
- 明确列出六个业务字段名。
- 说明 `sample_size` 未报告时为 `null`。
- 说明三个列表字段未报告时为空数组。

不要把 API Key 放进 body 或 prompt。

## 测试要求

至少覆盖：

1. `get_api_key` 返回传入 mapping 中的假 Key。
2. 参数化覆盖 Key 缺失、空字符串和纯空白，错误消息含 `DEEPSEEK_API_KEY` 且不包含 Key 内容。
3. Mock handler 验证 POST method、官方 host 和 `/chat/completions`。
4. 只验证 Authorization Header 等于基于假 Key 构造的预期值；不要打印 Header。
5. 验证请求 body 使用 `deepseek-v4-flash`，而不是旧模型名。
6. 验证 messages 的 role、用户摘要，以及 system prompt 包含 `JSON` 和六个字段名。
7. 验证 `response_format`、`thinking`、`stream` 和 `max_tokens`。
8. 验证请求 timeout 的 connect/read/write/pool 均为 30 秒。
9. 空摘要不会调用 handler，并抛出 `ValueError`。
10. Mock 成功响应原样作为 Python `object` 返回，不在本层解析 `choices`。
11. 401 响应通过 `raise_for_status()` 产生 `HTTPStatusError`，并验证状态码；暂不翻译错误。
12. Mock handler 抛出的 `ReadTimeout` 原样传播，并保留 request。

所有会发送请求的测试必须通过 `build_deepseek_client(fake_key, MockTransport(...))` 创建客户端。

## 验收标准

- 生产代码中不存在真实 Key、Key 前缀片段或 `.env` 读取。
- 测试不读取真实环境变量、不访问网络。
- 使用当前 `deepseek-v4-flash`，不使用已停用的旧模型名。
- 请求明确启用 JSON Output，并且 prompt 中也明确要求 JSON。
- HTTP 层返回 `object`，不提前解析模型文本。
- Authorization 不出现在 print、日志或异常消息中。
- Ruff、mypy strict 和 pytest 全部通过。

## 运行命令

```powershell
.\.venv\Scripts\ruff.exe check week03\lesson01_deepseek
.\.venv\Scripts\ruff.exe format --check week03\lesson01_deepseek
.\.venv\Scripts\mypy.exe --strict week03\lesson01_deepseek\deepseek_client.py week03\lesson01_deepseek\test_deepseek_client.py
.\.venv\Scripts\python.exe -m pytest week03\lesson01_deepseek\test_deepseek_client.py -q
```

## 完成后回复

```text
W3-01 完成
用时：
测试数：
Ruff：
mypy：
pytest：
本次使用的模型名：
为什么 JSON Output 仍不能代替业务校验：
为什么测试不读取真实 os.environ：
```
