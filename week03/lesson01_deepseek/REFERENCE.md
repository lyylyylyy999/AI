# W3-01 参考实现阅读指南

对应文件：`reference_solution.py` 和 `reference_tests.py`。参考答案独立于你的 `deepseek_client.py` 与 `test_deepseek_client.py`，用于任务通过后的复盘和对照，不覆盖学习实现。

## 1. 环境变量是显式依赖

`get_api_key()` 接收 `Mapping[str, str]`，不在函数内部直接访问 `os.environ`。

```text
CLI 入口以后可以传入 os.environ
自动化测试传入只含假 Key 的 dict
```

这既让测试结果不依赖机器配置，也防止测试意外接触真实密钥。缺失、空字符串和纯空白是三个不同输入，但都在发送请求前失败。

## 2. Client 只负责连接配置

`build_deepseek_client()` 集中配置：

- DeepSeek 官方 base URL；
- `Accept` 与 Bearer Authorization Header；
- 显式 30 秒 timeout；
- 可注入的 transport。

函数只构造客户端，不发送请求。测试通过注入 `MockTransport` 截获真正的 HTTPX Request。

## 3. 请求与响应是两个方向

```text
应用 → Mock handler：request
Mock handler → 应用：response
```

参考测试在 handler 内解析 `request.content`，证明客户端实际发送了 DeepSeek 请求契约。Mock response 使用另一份数据，证明测试没有把期望请求体伪装成响应，从而避免假阳性。

## 4. Prompt 契约必须对齐业务契约

System prompt 要求六个字段，并规定：

- `sample_size` 是正整数，未报告时为 `null`；
- 三个列表字段未报告时为空数组；
- 只返回 JSON，不附加解释。

这与第 2 周 `ResearchSummary` 的运行时校验保持一致。否则模型即使遵守 prompt，也可能生成必然无法通过业务校验的数据。

## 5. JSON Output 不是业务校验

```text
response_format={"type": "json_object"}
  → 约束模型生成合法 JSON 文本
  → 不保证六字段完整或字段类型正确
```

W3-01 只返回 `response.json()` 对应的 HTTP response `object`。`choices[0].message.content` 的提取属于 W3-02，模型文本的 `json.loads()` 与业务校验属于 W3-03。

## 6. HTTPX 异常保持原边界

- 401 已收到 HTTP Response，经 `raise_for_status()` 变为 `HTTPStatusError`。
- `ReadTimeout` 是传输阶段异常，保留原始 request。
- 当前层不翻译异常；完整错误矩阵留到第 4 周。

## 7. 自动化测试与真实冒烟

参考测试只使用假 Key 和 MockTransport，不访问网络、不产生费用。W3-01 通过后完成的单次真实冒烟只是额外验证外部服务当前兼容，不进入 pytest，也不替代自动化测试。

