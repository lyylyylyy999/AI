# 第 2 周学习看板：JSON、数据契约与 HTTP 基础

## 本周项目

为研究摘要结构化提取 CLI 建立本地数据与 HTTP 基础。本周不调用 DeepSeek，也不组装最终 CLI。

本周按“JSON → 业务数据契约 → HTTP 边界”推进。DeepSeek、模型响应解析和最终 CLI 分别留给第 3、4 周。

## 完成定义

- 能在 Python 对象、JSON 字符串和 UTF-8 JSON 文件之间转换。
- 能把未知 `object` 校验为完整六字段研究摘要契约。
- 能解释 TypedDict 与运行时校验的区别。
- 能使用同步 HTTPX 构造 GET、JSON POST 和显式 timeout。
- 自动化 HTTP 测试全部使用 MockTransport，不依赖真实网络。
- Ruff check、Ruff format --check、mypy strict 和 pytest 全部通过。

## 看板

| 卡片 | 目标 | 预计时间 | 状态 | 验收证据 |
|---|---|---:|---|---|
| W2-00 | 核对第 1 周基线与环境 | 20–30 分钟 | 已完成 | 学习实现与参考实现各 17 条测试通过；Ruff、mypy 通过 |
| W2-01 | Python 对象与 JSON 的转换 | 30–60 分钟 | 已完成 | 4 条测试通过；Ruff、mypy 通过；测试可从两个目录启动 |
| W2-02 | 定义研究摘要数据契约并做运行时校验 | 60–90 分钟 | 已完成 | 完整 6 字段契约；30 条学习测试通过；列表已复制 |
| W2-03 | 同步 HTTP 基础与 `httpx` 小练习 | 60–90 分钟 | 已完成 | HTTPX 0.28.1；8 条 Mock 测试及质量门通过 |
| W2-04 | 周末复盘、独立修改题与项目介绍 | 45–60 分钟 | 进行中 | 复盘回答、独立修改、质量门与阶段评分 |

## 范围控制

本周到 HTTP Mock 边界为止。不引入 DeepSeek、异步、Web 框架、数据库、LangChain 或过重的数据模型框架。后续内容按周拆分，不以提前完成阶段任务为目标。

## 安全约束

- 不读取或打印 `.env`、API Key 或 Authorization Header。
- 第 2 周所有 HTTP 测试均使用 MockTransport。
- 真实 DeepSeek 调用最早在第 4 周作为可选手动冒烟测试，并在调用前说明目的与请求次数。
