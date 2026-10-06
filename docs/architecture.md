# 架构与业务合同（目标设计，尚未全部实现）

## 架构

浏览器/API 文档 → FastAPI 路由 → 业务逻辑 → PostgreSQL；模型阶段由分析业务调用独立模型客户端。

首个业务任务先提供独立的上传统计流程：HTTP上传 → 字节/编码校验 → parse_lines → summarize → JSON响应。不进入数据库、不保存日志，完成后再发展持久化导入流程。该接口当前为待实现合同。

单个 `app` 包，逐步按数据模型、解析、业务、数据库访问、路由、模型客户端和页面组织。数据模型使用 Pydantic BaseModel，不依赖 FastAPI 或模型 SDK；路由不写 SQL，模型客户端不负责持久化。同步 FastAPI 路由配合同步 psycopg 与参数化 SQL；连接用上下文管理器，明确提交与回滚。

Conda LLM / Python3.12、FastAPI、Pydantic；PostgreSQL 与 psycopg 在数据库任务引入，DeepSeek 客户端在模型任务引入。Jinja2 与普通 HTML/CSS/JavaScript 提供同源页面。最终 Docker Compose 采用单应用实例与数据库，端口绑定127.0.0.1。

不加入 RAG、Agent、Redis、队列、ORM、复杂前端或公网账户系统。版本采用编号 SQL 迁移和版本记录，显式运行；启动不自动创建或重建数据库。

## 输入与数据一致性

- 每次导入是独立数据集，跨数据集不合并会话；原始字节 SHA-256 全局唯一，重复导入返回409，由数据库唯一约束保护并发。
- UTF-8 JSONL，允许空白行，非空行恰有 `conversation_id`、`role`、`content`。三者是字符串；ID和正文不允许纯空白；角色为 system/user/assistant。不裁剪正文和 ID。
- 文件限制2 MiB，非空消息最多10,000条。按限额读取，拒绝空数据集；JSONL 错误包含物理行号与安全类别，不回显原文或用户字段名。
- 原日志没有时间戳或消息 ID；按出现顺序排序，同一文件内相同消息允许出现，不做推测去重，不提供消息日期趋势。
- 校验完成后才进入导入事务，数据集、会话与消息整体写入/回滚；原始上传文件不持久化，只存哈希、元信息与解析正文。
- 正文不可修改；修正需删除并重新导入。删除数据集级联删除消息、会话与分析，不保留原文副本。

四类实体：数据集（ID、名称、哈希、导入时间），会话（ID、数据集、原始会话 ID），消息（ID、会话、出现顺序、角色、正文），分析记录（ID、会话、状态、结果、版本/配置、用量、耗时、安全错误码）。内部 ID 使用 UUID，时间使用 UTC timezone-aware 时间。

约束：数据集哈希唯一；数据集内原始会话 ID 唯一；会话内消息顺序唯一；角色受约束；外键级联删除。消息序号按该会话出现次序从1开始。

上传统计接口使用现有 Python summarize；数据库数据集统计用 SQL。二者均返回 total_messages、conversation_count、messages_by_role（三角色均存在）、total_characters。字符数与 Python len(content) 一致，含空白，不是 token 数。

## API 合同

业务前缀 `/api/v1`。路径使用内部 UUID。列表使用 offset≥0、limit默认20且最大100；集合返回 items、total、offset、limit。数据集按导入时间和ID排序，会话按原始ID和内部ID排序，消息按序号排序，分析按创建时间和ID排序。

| 方法与路径 | 行为 |
| --- | --- |
| POST /logs/statistics | multipart必填file；200返回统计，不保存、不去重；详细边界见TASK-001 |
| POST /datasets | multipart 文件及显示名称；201返回数据集元信息与导入统计 |
| GET /datasets | 数据集列表 |
| GET /datasets/{id} | 数据集详情 |
| DELETE /datasets/{id} | 级联删除，成功204，不存在404 |
| GET /datasets/{id}/conversations | 支持原始 conversation_id 精确筛选 |
| GET /conversations/{id}/messages | 支持 role 筛选，返回有序消息 |
| GET /datasets/{id}/statistics | 数据集统计 |
| POST /conversations/{id}/analyses | 模型阶段加入，同步主动分析，成功201，返回分析记录 |
| GET /conversations/{id}/analyses | 模型阶段加入，只查询历史，无付费副作用 |

统一业务错误包含 code、message、request_id：404不存在、409重复、413超字节限额、422非法输入/数量限额、503数据库不可用或模型未启用。框架校验错误也需转换，不能包含原输入。请求追踪任务实施前，健康端点不使用这一错误合同。

`/health` 仅表示进程存活；数据库阶段增加 `/ready` 验证数据库，模型关闭不影响后端就绪。不通过 GET 执行分析。

## 模型阶段

默认关闭，通过环境变量明确启用并配置密钥和模型名。采用 DeepSeek Chat Completions JSON Output，再以 Pydantic 验证 summary、key_points、action_items；无行动项允许空列表。

会话按顺序序列化为 JSON 数据，不将原日志 system 内容作为应用系统指令。序列化输入最多20,000字符，超限返回422，不截断。保留明确的系统指令和数据边界，不声称这能彻底消除提示注入。

30秒超时、最多2000输出 token、自动重试关闭。空输出、截断、Schema错误等返回502并记录独立错误码；上游限流503、超时504；不回显上游异常。模型名不硬编码，记录实际配置。

先以短事务创建 running 记录并释放连接，再请求模型，随后以新事务保存 succeeded/failed。启动时将单实例遗留 running 标记 interrupted；结束保存失败不得向用户报告持久化成功。并发删除导致分析所属会话消失时返回404，不恢复已删除数据。首版不自动补偿或自动再次付费调用。

记录输入哈希、提示词版本、模型与参数、响应身份、用量和耗时；缺失用量为 null。真实模型验证由学习者显式开启，不能因为检测到密钥而运行。关闭时分析返回503，其余接口正常。

## 展示与评测

页面：导入、列表、详情、统计、主动分析与历史结果；删除明确确认，忙碌时防重复点击，所有用户和模型文本安全转义，不插入未经转义的 HTML。

默认本地、合成数据、无公网账户。Docker 和页面只在交付阶段引入。录屏区分真实调用与离线样例。

评测20–30条人工核验合成对话，调试/保留测试集分开；失败计入总体分母，区分规则评分、人工事实检查和真实模型验证。报告版本、运行条件、限制与真实耗时/用量，费用注明价格日期和来源。
