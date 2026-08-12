# 第 2 周复盘与检查点

预计用时：45–60 分钟。本次不学习 DeepSeek，不查看参考实现，不提交 Git。

## A. 概念复盘（15 分钟）

请用自己的话回答：

1. `json.load` 成功后，为什么返回值仍不能直接视为 `ResearchSummary`？
2. `TypedDict` 与运行时校验分别解决什么问题？
3. 为什么 `sample_size=True` 必须拒绝？
4. 为什么校验后的三个字符串列表要与输入列表解除引用共享？
5. `Accept` 与 `Content-Type` 分别描述什么？
6. `HTTPStatusError` 与 `RequestError` 的边界是什么？

## B. 独立修改题：GET query parameter（20–30 分钟）

在 W2-03 的学习实现中，为 `fetch_service_info` 增加关键字参数 `language`：

```text
默认值：zh
调用形式：fetch_service_info(client, language="en")
请求目标：GET /v1/info?lang=en
```

要求：

- 使用 HTTPX 的 `params=` 参数，不手工拼接 `?lang=`。
- `language` 为空或纯空白时，在发送请求前抛出 `ValueError`。
- 原有调用 `fetch_service_info(client)` 保持有效，默认发送 `lang=zh`。
- 新增测试验证 path 与 query parameter。
- 新增测试证明空语言不会调用 Mock handler。
- 原有 8 条测试继续通过。

本题不提供逐步代码提示。若 30 分钟仍未完成，停止并记录阻塞点，不延长为新的两小时任务。

## C. 项目介绍训练（5 分钟）

准备一段 90 秒以内的介绍，说明：

1. 第 2 周解决了什么问题？
2. JSON 语法解析与业务校验如何分层？
3. 为什么自动化 HTTP 测试不访问网络？
4. 当前还没有完成哪些能力？

## D. 质量门（5–10 分钟）

```powershell
.\.venv\Scripts\ruff.exe check week02
.\.venv\Scripts\ruff.exe format --check week02
.\.venv\Scripts\mypy.exe --strict week02\lesson01_json\json_practice.py week02\lesson01_json\test_json_practice.py week02\lesson02_validation\research_schema.py week02\lesson02_validation\test_research_schema.py week02\lesson03_http\http_client.py week02\lesson03_http\test_http_client.py
.\.venv\Scripts\python.exe -m pytest week02\lesson01_json\test_json_practice.py week02\lesson02_validation\test_research_schema.py week02\lesson03_http\test_http_client.py -q
```

## 完成后回复

```text
第 2 周复盘完成
A1：
A2：
A3：
A4：
A5：
A6：
独立修改用时：
新增测试数：
Ruff：
mypy：
pytest：
90 秒项目介绍：
本周最薄弱的两个点：
```
