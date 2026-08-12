# W2-03 参考实现阅读指南

对应文件：`reference_solution.py` 和 `reference_tests.py`。

## 阅读重点

### 1. Client 是配置与资源边界

`build_client()` 集中保存 base URL、默认 Header、timeout 和 transport。调用方使用 `with` 关闭客户端，测试则通过 transport 参数注入 MockTransport。

### 2. MockTransport 验证真实 Request

Mock handler 收到的是 HTTPX 真正构造出的 `Request`。因此测试可以验证 method、URL、Header、序列化后的 body 和 timeout，而不需要连接服务器。

这比只 Mock `submit_abstract()` 的返回值更有价值，因为后者无法证明请求是否正确构造。

### 3. 两类失败边界

```text
服务器返回 404/429/500
  → 已经存在 Response
  → raise_for_status()
  → HTTPStatusError

连接、网络或 timeout 失败
  → 请求没有正常完成
  → RequestError 的具体子类
  → 例如 ReadTimeout
```

`HTTPStatusError` 同时携带 request 和 response；`RequestError` 携带 request，但通常没有可用的业务 response。

### 4. HTTP 层返回 object

`response.json()` 只把 JSON 转成 Python 值。顶层可能是字典、列表、字符串、数字、布尔值或 `None`。即使得到字典，也不能证明它符合研究摘要契约。

后续组合方式是：

```text
response.json() → object → validate_research_summary() → ResearchSummary
```

### 5. 当前刻意不做的事情

- 不捕获并翻译 HTTPX 异常。
- 不加入 Authorization Header。
- 不调用真实服务。
- 不使用异步 API。

这些边界会在 DeepSeek 客户端阶段逐步加入。
