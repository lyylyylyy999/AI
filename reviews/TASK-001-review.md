# TASK-001 接口测试与中间审查

日期：2026-10-06。审查范围：`d706a61..6150235` 完整差异及当前工作区。工作区原有 app/test.py、.pytest_tmp 不属于本次测试修改。未改生产代码、未调用模型、未操作数据库、未提交。

## 测试证据

新增 tests/test_upload_statistics.py，34个场景，走真实 TestClient multipart 上传。多数测试不Mock业务；限额观测保留真实解析，文件观测保留框架真实上传文件；意外异常用Mock验证500与释放。

当前接口测试：12 passed、22 failed。失败按合同与实现差异保留，不按实现降低断言。错误响应形状不符合合同导致多个用例失败，不等于22个独立缺陷。

测试自身初版的响应类型和大数据参数ID问题已修正；当前无fixture错误，mypy通过。与生产失败分开处理。

## 严重问题

- app/main.py 的默认请求校验错误未脱敏：将 file 字段作为普通字符串提交，错误响应包含原字符串 input。使用 secret-marker 确认数据实际进入框架错误路径。合同要求禁止输入回显。

## 主要问题

- app/main.py 的错误仍是 detail 字符串或默认ValidationError列表，没有顶层 code/message/request_id；解析错误没有独立line_number；响应缺X-Request-ID。缺字段、非法数据、限额失败与请求ID测试捕捉这些问题。
- 上传路由调用 file.file.read()，先无界读取后检查长度。观察真实上传文件的read参数为-1；应限制读取量再判断大小。
- text.splitlines() 把正文中的合法U+2028/U+0085当成物理换行，合法JSONL返回422。应保持文件物理行边界。
- list(parse_lines(...)) 在检查10,000条前消费全部记录。观测10,002条均被消费；超限后若有非法行，返回invalid_json而不是先遇到的too_many_messages。应在逐条消费时执行限额，达到第一条超限即停止。

## 次要问题

- 应用description仍写“尚未实现日志导入”，与已有上传统计接口不一致。持久化尚未实现，描述应准确区分。

## 缺失的测试

本任务关键成功、错误、字节/条数边界、Unicode行边界、请求ID、脱敏和资源释放已覆盖，无需要为完成当前修复新增的核心场景。修复若引入新机制，再按差异补回归测试。

## 合理的设计

- 复用parse_lines与summarize，使用Statistics作为响应模型，没有重复评分或统计代码。
- 同步路由没有直接在异步事件循环中执行阻塞读取。
- 标准样例、多会话、角色零计数、恰好字节/数量限额和重复上传通过。
- 上传文件在成功、预期错误及合成内部错误后均被框架关闭，当前资源关闭测试通过；不应仅因路由没有显式finally就断言泄漏。
- 合成内部错误仍返回500，未被伪装成422，错误消息未回显。

## 修复顺序与提示1

1. 先梳理错误返回与请求ID的共同出口，区分业务错误和框架请求校验错误，只返回安全字段。
2. 检查“先读取再判断”的顺序：字节和条数都应在读取/消费过程中限制。
3. 比较JSONL物理行与字符串splitlines认可的Unicode分隔符，选用保留物理行的文本迭代方式。

这是中间审查，不生成最终复盘问题，也不标记任务完成。学习者修改生产代码后重新运行同一测试集，再进行最终审查。

## 修复后复查（2026-10-06）

学习者明确要求按本记录修正代码，本轮由导师实施。保持 main，未提交。审查基线仍为 d706a61，已检查基线至 HEAD 的完整差异、暂存和工作区变更；app/test.py、requirements-dev.txt 等原有改动保留。

- 严重问题：原记录中的框架校验输入回显已修复，本轮修复范围内无遗留。
- 主要问题：错误体改为安全的 code/message/request_id，解析错误单独附 line_number；服务端生成 UUID，成功、预期失败和意外500响应均带 X-Request-ID。有界读取保留，消息逐条解析，到第10,001条立即拒绝；使用 StringIO 的通用物理换行迭代，正文 Unicode 分隔字符不再被拆行。本轮修复范围内无遗留。
- 次要问题：应用 description 已更新。另发现 pytest.ini 的 testpaths 仍指向旧 week01/diagnostic，且覆盖 pyproject.toml 的默认配置；本轮未修改该既有配置，验证必须显式指定 -c pyproject.toml。
- 缺失测试：当前修复范围无。补充 LF/CRLF/CR 的错误行号场景，并加强健康端点、意外500响应的请求ID断言。
- 合理设计：保留 parse_lines、summarize 和同步上传路由；列表最多保存10,000条合法消息，完整校验后才统计。上传资源继续由框架释放，真实 multipart 资源观测覆盖成功、预期失败和内部错误。意外异常返回安全500，未转为422。

实际解释器：D:\Anaconda_envs\envs\LLM\python.exe（Python3.12.13）。执行命令与结果：

```powershell
& 'D:\Anaconda_envs\envs\LLM\python.exe' -m pytest -c pyproject.toml -q
# 81 passed，其中上传接口37个场景。
& 'D:\Anaconda_envs\envs\LLM\python.exe' -m ruff check .
# All checks passed!
& 'D:\Anaconda_envs\envs\LLM\python.exe' -m mypy
# Success: no issues found in 10 source files
git diff --check
# 通过，无空白错误。
```

关键断言仍按合同保留：敏感标记确实进入框架校验和非法记录路径；字节限额观测真实 read 参数；数量限额观测实际解析产出，不仅检查响应状态；资源关闭观测框架创建的真实上传文件。内部错误仅 Mock summarize 来触发500，未 Mock 上传与释放流程。这些测试不证明框架进入路由前的全请求流量限制。

代码复查及离线自动检查通过；学习者在 /docs 的手动上传验收、关键测试解释与复盘尚未完成，不标记 TASK-001 完成。复盘问题：

1. 为什么读取2 MiB + 1字节，而不是只读取2 MiB？这与框架接收整个 multipart 请求的限额有什么区别？
2. 为什么第10,001条合法消息后立即停止？若非法行出现在它之前或之后，错误码分别应该是什么？
3. 为什么 StringIO 保留的物理行边界能解决 U+2028/U+0085 问题？正文里的转义换行是否应改变 line_number？
4. 为什么框架校验错误不能直接返回 exc.errors()？内部错误测试中的 Mock 能证明什么，不能证明什么？
