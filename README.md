# 对话日志管理与统计服务

一个从基础后端逐步演进为 AI 应用的训练项目。最终支持 JSONL 导入、会话查询、统计、主动模型分析和轻量页面，本地演示，不开放公网。

**当前状态：JSONL上传统计接口、解析、校验、统计及请求追踪基础模块已就绪。HTTP层支持 `/health`、`POST /api/v1/logs/statistics` 和 API 文档；上传仅返回统计，不保存日志。数据库、持久化导入、模型与页面尚未实现。** 原训练仓库保持不变，本项目不依赖原仓库运行。这里只保存项目代码，不归档全部训练材料。

## 开始运行（PowerShell / Conda LLM）

```powershell
cd C:\Users\Lenovo\Desktop\AI
conda activate LLM
python -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000
```

统一使用 Conda `LLM` 环境，当前 Python 为3.12.13，所需依赖已经存在，本次未安装或升级环境中的包。环境路径为 `D:\Anaconda_envs\envs\LLM`。若 PowerShell 尚不能激活 Conda，可直接用 `& 'D:\Anaconda_envs\envs\LLM\python.exe' -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000`，不用修改全局 Shell 配置。

打开 http://127.0.0.1:8000/docs 查看接口；`/health` 返回 `{"status":"ok"}`，仅说明进程存活，不证明数据库、模型或业务可用。当前不需要环境变量、模型密钥或数据库。

`.env.example` 仅记录配置合同，不会自动加载；对应配置会在后续任务增加。运行依赖与开发依赖分别固定本次验证过的直接依赖版本，Python 基线为3.12。不导出整个 LLM 环境，不引入与项目无关的包；传递依赖尚未完整锁定。新环境需要时再运行 `python -m pip install -r requirements-dev.txt`，现有环境不用重复安装。

## 验证

```powershell
conda activate LLM
python -m pytest
python -m ruff check .
python -m mypy
git diff --check
```

测试覆盖最小入口、解析、统计与请求追踪模块。默认排除 database 与 live_model 标记的测试；后续数据库与真实模型验证将提供单独的显式入口，存在密钥不代表允许调用。模型质量和独立交付能力不能由离线测试数量证明。

验证使用 `D:\Anaconda_envs\envs\LLM\python.exe`；实际结果见[迁移登记](docs/migration.md)。解析通过不等于导入事务或数据库能力完成。

## 项目导航

- [协作规则](AGENTS.md)：分工、审查、Git、质量要求。
- [路线图](ROADMAP.md)：阶段门槛和每周容量。
- [架构与业务合同](docs/architecture.md)：数据语义、API、依赖方向和模型边界。
- [迁移登记](docs/migration.md)：原任务来源与迁移状态。
- [当前任务](tasks/TASK-001-upload-statistics.md)：把已有解析与统计接入 FastAPI；先返回统计，不保存日志，数据库随后引入。
- [任务模板](tasks/templates/task-template.md)、[复盘模板](retrospectives/template.md)、[每周复盘模板](weekly/template.md)。

每周15小时：实现与调试8小时、测试审阅与审查修改3小时、LLM 基础3小时、复盘1小时。你实现生产代码，我设计任务、编写测试并审查。只详细设计下一个任务。

Git 当前使用 `main`；初始化没有自动提交。首个提交完成后，将其记录为 TASK-001 审查基线；之前以全部新增文件为初始化审查范围。
