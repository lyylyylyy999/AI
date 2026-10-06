# 项目能力迁移记录

源仓库 `C:\Users\Lenovo\Desktop\LLM-learn` 保持不变，仅作来源参考。源 HEAD：`d695dd6e49c7c6124f79749aadac240b796340a5`。不建立运行依赖，不搬运历史任务、复盘或整个练习目录。

| 来源 | 项目目标 | 状态与调整 |
| --- | --- | --- |
| 原 TASK-001 数据类与统计 | app/domain.py | 已迁移；统一安全错误类别，简化计数，保留原文和空输入全零行为 |
| 原 TASK-001 文件解析 | app/jsonl.py | 已迁移；分离行解析与文件读取，返回物理行号，不回显输入，不保留输出文件 main |
| 原 TASK-004 请求追踪 | app/tracing.py | 已迁移；保留 clock/sink 与异常记录能力，暂未接入 HTTP 中间件 |
| 原 TASK-004 测试 | tests/test_tracing.py | 更新项目导入路径，验证正常、异常与生命周期 |
| 原 TASK-009 应用工厂思路 | app/main.py | 仅采用工厂组织方式；新健康接口，不迁模型专用路由 |

2026-10-06 按学习者要求，Message、Statistics 与 TraceRecord 已从 dataclass 改为 Pydantic BaseModel，序列化使用 model_dump/model_dump_json。TraceRecord 保持冻结；Message 严格校验、禁止额外字段，不裁剪正文。直接模型构造失败使用 ValidationError，JSONL边界转换为安全 InvalidMessageError，并保留原错误优先级与行号。错误字符串隐藏输入；程序也不应直接记录 ValidationError.errors() 的默认输入详情。

TASK-001 源文件最近修改提交：`b140e0fa1d42bd101b5ee196d907fae6b783307a`。解析项目测试根据新合同编写，覆盖脱敏、顺序、迭代器、优先级、文件关闭与标准文件异常。迁移来源和文件哈希见 migration-manifest.json。

重试、异步批处理、模型客户端和评测流水线暂不迁移：当前项目没有这些运行需求。后续根据模型与评测任务的实际合同抽取所需部分。

项目尚无数据库或模型调用，只有独立基础模块与健康接口。空数据集拒绝、限额与原子导入在业务任务实现，不能把基础统计的空输入行为当作导入成功。

## 验证

2026-10-05 使用 Conda LLM / Python3.12.13 验证：`python -m pytest -q` 为 **43 passed**；Ruff通过；mypy检查5个源码文件通过；Git差异检查通过。未调用模型，未安装或升级依赖。43项只验证当前基础模块，不证明数据库或模型功能已实现。

2026-10-06 Pydantic改造后验证：**44 passed**；Ruff、mypy与Git差异检查通过，迁移目标哈希已更新。没有新增依赖；上传统计接口仍待 TASK-001 实现。
