# W3-03：模型 JSON 解析与业务校验

预计用时：60–90 分钟。本任务接收 W3-02 已提取出的模型文本，把它解析并校验为第 2 周的 `ResearchSummary`。不发送 HTTP 请求，不组装 CLI，不设计完整错误码矩阵。

## 本课目标

完成后你应当能够：

1. 区分 HTTP response JSON 与模型生成的 JSON 文本。
2. 对普通 JSON 文本和 Markdown code fence 做最小预处理。
3. 用 `json.loads()` 把模型文本解析为未知 Python `object`。
4. 复用 `validate_research_summary()` 完成业务校验，不复制校验逻辑。
5. 区分 JSON 语法错误、顶层类型错误和业务字段错误。

## 本课数据流

```text
HTTP response JSON
→ W3-02: choices[0].message.content
→ 模型 JSON 文本 str
→ W3-03: json.loads
→ object
→ validate_research_summary
→ ResearchSummary
```

W3-03 从“模型 JSON 文本”开始，不再次解析 `choices`。最终 CLI 和完整异常翻译留到第 4 周。

## 独立任务

在本目录创建：

- `model_json_parser.py`
- `test_model_json_parser.py`

实现：

```python
from week02.lesson02_validation.research_schema import ResearchSummary


def parse_research_summary_content(content: str) -> ResearchSummary: ...
```

使用已有校验器：

```python
from week02.lesson02_validation.research_schema import (
    ResearchSummary,
    validate_research_summary,
)
```

不要复制六字段校验逻辑，也不要通过修改 `sys.path` 导入模块。

## 模型文本预处理规则

### 普通 JSON 文本

允许文本两端存在空白：

```text
  {"research_question": "问题", ...}\n
```

外层空白可以在解析前去除。

### Markdown code fence

至少支持模型常见的完整包裹形式：

````text
```json
{"research_question": "问题", ...}
```
````

也支持没有语言标签的完整 fence：

````text
```
{"research_question": "问题", ...}
```
````

只在整个非空内容被开头 fence 和结尾 fence 完整包裹时移除 fence。不要用 `strip("`")`，它会把不完整或意外的反引号也静默删除。

### 空内容

以下输入在调用 `json.loads()` 前抛出 `ValueError`：

- `""`
- 纯空白
- fence 内部为空或纯空白

错误消息至少包含 `content`。

## 解析与校验规则

1. 预处理得到 JSON 文本。
2. 调用 `json.loads()`。
3. 把返回值显式视为 `object`，不要让 `Any` 穿透边界。
4. 调用 `validate_research_summary(parsed)`。
5. 返回经过校验的新 `ResearchSummary`。

本任务允许以下现有异常原样传播：

- 非法 JSON：`json.JSONDecodeError`
- JSON 顶层不是 object：校验器产生的 `TypeError`
- 字段缺失：校验器产生的 `ValueError`
- 字段类型、列表元素错误：校验器产生的 `TypeError` 或 `ValueError`

不要在本周建立自定义异常体系或完整错误矩阵。

## 测试要求

至少覆盖：

1. 正常六字段 JSON 文本返回 `ResearchSummary`。
2. 返回的列表与解析前数据不共享可变引用，由既有校验器负责复制。
3. 带 `json` 标签的 Markdown code fence。
4. 不带语言标签的 Markdown code fence。
5. 空字符串、纯空白、空 fence。
6. 非法 JSON，并确认是 `json.JSONDecodeError`。
7. JSON 顶层为列表或其他非 object 值。
8. 六字段中的字段缺失。
9. `sample_size` 或字符串字段类型错误。
10. 三个列表字段的元素类型错误。

测试应直接调用 `parse_research_summary_content()`，不访问网络，不调用 W3-01 客户端，也不重新测试 W3-02 的所有响应结构错误。

## 验收标准

- 公开接口是 `parse_research_summary_content(content: str) -> ResearchSummary`。
- 普通 JSON 与两种完整 code fence 均可处理。
- 空内容在 JSON 解析前失败。
- `json.loads()` 的结果显式收窄为 `object`。
- 业务校验只复用 `validate_research_summary()`，没有重复实现。
- JSON 语法、顶层结构和业务契约三个错误层次保持分离。
- 不提前创建 CLI、自定义错误矩阵、异步代码或框架集成。
- Ruff、mypy strict 和 pytest 全部通过。

## 运行命令

```powershell
.\.venv\Scripts\ruff.exe check week03\lesson03_model_json
.\.venv\Scripts\ruff.exe format --check week03\lesson03_model_json
.\.venv\Scripts\mypy.exe --strict week03\lesson03_model_json\model_json_parser.py week03\lesson03_model_json\test_model_json_parser.py
.\.venv\Scripts\python.exe -m pytest week03\lesson03_model_json\test_model_json_parser.py -q
```

## 完成后回复

```text
W3-03 完成
用时：
测试数：
Ruff：
mypy：
pytest：

HTTP response JSON 与模型 JSON 文本有什么区别：
为什么 json.loads 的结果仍标注为 object：
为什么不能复制 validate_research_summary 的逻辑：
为什么 code fence 处理不能使用 strip("`")：
```

