# 第 2 周学习评估

## 结论

第 2 周检查点：通过。

本周完成了从本地 JSON 到可靠 HTTP 请求边界的学习闭环。尚未调用 DeepSeek，也尚未组装最终 CLI；这些内容按容量调整后分别安排在第 3、4 周。

## 实际质量证据

- Ruff check：通过。
- Ruff format：24 个文件格式正确。
- mypy strict：6 个学习文件无问题。
- pytest：45 条学习测试通过。
- HTTP 自动化测试全部使用 MockTransport。
- Codex 验收使用独立 basetemp，未占用 `.pytest_tmp`。

## 分项评分

| 维度 | 得分 | 评价 |
|---|---:|---|
| JSON 与数据边界 | 23/25 | 能完成字符串、文件和 Python 对象往返；需继续巩固“解析成功不等于业务有效” |
| 类型契约与运行时校验 | 22/25 | 能处理字段、元素、bool 边界和列表复制；TypedDict 的静态职责仍需反复表达 |
| HTTP 与错误边界 | 18/25 | 能构造 GET/POST、Header、timeout 和 Mock；HTTPStatusError 与 RequestError 的口头区分仍不稳定 |
| 测试与代码质量 | 24/25 | 45 条测试及全部质量门通过；能够根据反例补强测试证据 |
| 项目表达 | 8/10 | 能说明数据分层与 Mock 价值；可增加具体接口、异常和测试数字 |
| 总分 | 95/110 | 折算 86/100，通过 |

## 概念订正

1. `json.load()` 返回普通 Python 对象，而不是“JSON 格式”；顶层类型可能是字典、列表、标量或 `None`。
2. `TypedDict` 描述静态字段形状，运行时不会自动验证或转换数据。
3. `HTTPStatusError` 表示已经收到非成功 HTTP 响应；`RequestError` 表示请求或传输阶段失败。
4. HTTP 层返回 `object`，业务校验层才把未知值收窄为 `ResearchSummary`。

## 独立修改评价

成功为 GET 请求加入 `language` 参数：

- 默认发送 `lang=zh`。
- 支持自定义语言。
- 使用 `params=`，没有手工拼接 URL。
- 空白语言在发送请求前失败。
- 测试直接证明默认值、自定义值和“不发送请求”。

非阻塞改进：`language` 已标注为 `str`，因此实现中的 `language is not None` 判断与公开类型契约不一致，可以简化为 `if not language.strip()`。

## 当前薄弱点

1. HTTP 概念尚未形成稳定心智模型，需要在第 3 周继续通过请求、响应和异常实例巩固。
2. 代码实现速度偏慢，但目前主要原因是新概念和严格测试要求；下一周优先练习复用既有模式，不追求一次写对。
3. 口头表达有时把静态类型、运行时对象和数据格式混在一起，需要坚持使用“JSON 文本 → Python object → 业务校验”这条数据流描述。

## 第 3 周入口

进入 DeepSeek V4 Mock 客户端与模型响应解析。自动化测试继续使用假 Key 和 MockTransport，本周不进行真实付费请求。
