# TASK-001 — FastAPI 上传日志并返回统计

- 难度：L2
- 预计有效编码时间：2–3小时；依赖准备、阅读与审查修改另计
- 分支：main
- 状态：待学习者实现
- 审查基线：仓库尚无提交；首次提交后记录任务说明提交 SHA，此前检查全部新增文件
- 已有基础：app/jsonl.py 的 parse_lines、app/domain.py 的 summarize 已完成并验证

## 背景

将已完成的日志处理能力接到 HTTP，先做出一个可在 /docs 上传文件、查看结果的业务接口。这个阶段不保存日志，也不需要数据库或模型。

## 学习目标

- 理解 multipart 文件上传与普通 JSON 请求的区别。
- 用薄路由调用已有解析与统计，避免重复业务逻辑。
- 明确输入限额、完整校验、错误响应和上传资源释放。

## 前置知识

阅读 FastAPI [文件上传](https://fastapi.tiangolo.com/tutorial/request-files/) 中 UploadFile 与同步处理方式，以及[错误处理](https://fastapi.tiangolo.com/tutorial/handling-errors/)。复习字节与 UTF-8 文本、生成器延迟失败、HTTP 200/413/422。

执行前使用 `conda activate LLM`。当前该环境缺少 python-multipart；它是 multipart 文件上传需要的新增依赖。实施时在 LLM 中只安装该依赖，验证后固定版本到 requirements.txt，不升级现有包。本次任务设计尚未安装依赖。

## 功能要求

### 1. 请求与成功响应

新增 `POST /api/v1/logs/statistics`。请求为 multipart/form-data，必填字段 `file`，接收一份 UTF-8 JSONL 文件。不要用服务器文件路径作为请求参数；不按文件扩展名或客户端 Content-Type 判断数据有效性。

成功返回200，响应字段：

```json
{
  "total_messages": 3,
  "conversation_count": 1,
  "messages_by_role": {"system": 1, "user": 1, "assistant": 1},
  "total_characters": 6
}
```

对应三条正文分别为“系统”“你好”“收到”，同一 conversation_id。字符数包含原文空白，不是 token 数。

### 2. 处理与限额

- 使用同步路由，读取上传对象的同步文件接口；最多读取 2 MiB + 1 字节，用来区分恰好等于限额与超过限额，不无界读取。
- 严格 UTF-8 解码。首版不支持 UTF-8 BOM，不自动修复编码或非法 JSON。
- 调用现有 parse_lines 与 summarize，不改写其校验或计数。传入保留物理行边界的文本迭代器，不手工 split 破坏行号。
- 最多10,000条非空消息，恰好上限允许，超限拒绝。实现数量限制时不可先无界转为列表。
- 空文件或仅空行返回422；保持底层 summarize 的空输入全零行为不变。
- 完整消费并验证后才返回成功。前面合法、后面非法时不返回部分统计。
- 成功和异常路径均释放上传资源。不保存原文件或正文，不创建业务数据文件，不连接数据库，不调用模型。

说明：读取限额针对上传文件内容，框架处理 multipart 时可能使用临时缓冲或临时文件；本任务不实现 HTTP 全请求流量限制，不声称请求体在进入路由前已被限制。

### 3. 错误合同

每次请求生成服务端 UUID request_id，响应头带 X-Request-ID；错误体顶层返回 code、message、request_id，解析错误额外返回 line_number。不信任外部传入的 request_id。

| 场景 | HTTP | code |
| --- | --- | --- |
| 缺少 file 或上传字段不是文件 | 422 | invalid_request |
| 文件超过2 MiB | 413 | file_too_large |
| 非法 UTF-8 | 422 | invalid_encoding |
| 空文件或只有空行 | 422 | empty_log |
| 超过10,000条消息 | 422 | too_many_messages |
| JSONL非法记录 | 422 | 使用 InvalidMessageError 原有 code，附物理行号 |

按实际处理顺序检查：缺字段 → 字节限额 → 解码 → 逐条解析和数量限制 → 空集。非法行早于数量超限时报告该非法行；先超过数量上限则立即拒绝。

message 使用固定安全描述，不回显文件名、字段值、原文、ValidationError输入或异常 traceback。框架请求校验错误也转换为上述安全合同。不要捕获所有异常并伪装成422；意外错误保留服务器错误语义。

## 约束

- 在现有 create_app 中注册；保持 /health 和 /docs 可用。
- 复用业务模块；Message、Statistics 已使用 Pydantic BaseModel，可直接使用 Statistics 作为 response_model。基础domain不导入FastAPI；序列化使用 model_dump，不再使用 dataclasses.asdict。
- 只增加完成本任务需要的路由、响应模型和辅助代码，不建立空的多层目录。
- 不加入数据库、模型、鉴权、前端、批量文件或持久化去重。再次上传同一文件仍正常返回统计。

## 验收标准

- 在 /docs 上传上述三条样例，得到200和准确统计。
- 多会话、缺某种角色、正文含空白时统计正确，三角色始终存在。
- 缺文件、编码错误、空日志、非法行按合同返回。
- 两空行之后第3行非法记录，line_number为3；原文敏感标记不出现在错误响应中。
- 字节/数量恰好上限允许，超过上限拒绝；错误不能返回部分成功。
- 不依赖数据库或密钥；/health不退化；上传资源在成功和失败后关闭。

## 测试要求

你实现生产代码并手动验证，再通知我编写接口测试。导师用 TestClient 上传内存文件，验证真实multipart路径，不调用模型或数据库。

测试覆盖成功统计、三个角色零计数、原文字符计数、重复请求、缺file、错误类型、空日志、错误行号、UTF-8、字节与条数边界、晚出现非法行、请求ID及脱敏。资源释放检查需要证明失败也进入释放路径。

使用 Conda LLM 运行 pytest、Ruff、mypy 和 git diff --check，记录实际命令与结果。现有43项测试通过不能证明新接口完成。

## 边界情况

文件名不可信，不拼接磁盘路径；正文空白不裁剪；无消息时间戳，不新增时间统计；多次调用不留下业务状态。

## 进阶任务

无。数据库建模在本任务最终审查后单独设计。

## 完成定义

功能、手动验证、接口测试与最终审查通过，无严重遗留；提出3–5个针对性问题并完成简版复盘。建议提交：`feat: add uploaded log statistics endpoint`。
