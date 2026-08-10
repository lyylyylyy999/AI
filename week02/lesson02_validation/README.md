# W2-02A：从未知 JSON 到核心数据契约

预计用时：45–75 分钟。本任务不访问网络，不安装依赖，也不修改 W2-01。

## 目标

实现一个运行时校验函数，把未经信任的 `object` 转换成具有明确类型的研究摘要核心数据。

完成后你应能区分：

- JSON 语法解析：文本是否符合 JSON 语法。
- 业务数据校验：字段是否存在、类型和值是否合理。
- 静态类型检查：mypy 根据类型标注检查代码，但不会自动检查运行时数据。

## 本次数据契约

在 `week02/lesson02_validation/research_schema.py` 中定义：

```python
from typing import TypedDict


class ResearchSummaryCore(TypedDict):
    research_question: str
    data_source: str
    sample_size: int | None
```

含义如下：

| 字段 | 允许的值 |
|---|---|
| `research_question` | 去除首尾空白后仍非空的字符串 |
| `data_source` | 去除首尾空白后仍非空的字符串 |
| `sample_size` | 正整数或 `None` |

`None` 表示摘要没有报告样本量。注意：Python 中 `bool` 是 `int` 的子类，因此 `True` 不应被当成样本量 `1` 接受。

## 独立任务

实现：

```python
def validate_summary_core(data: object) -> ResearchSummaryCore: ...
```

验证顺序：

1. 顶层必须是字典，否则抛出 `TypeError`。
2. 三个必需字段必须全部存在，缺少任意字段都抛出 `ValueError`。
3. 两个文本字段类型错误时抛出 `TypeError`，空字符串或纯空白字符串抛出 `ValueError`。
4. `sample_size` 类型错误（包括布尔值）时抛出 `TypeError`，整数小于等于零时抛出 `ValueError`。
5. 校验通过后构造并返回一个新的 `ResearchSummaryCore`。

不要使用 `assert` 校验外部数据；`assert` 用于开发期内部假设，可能在优化模式下被禁用。不要用 `str(value)` 或 `int(value)` 静默修复错误类型。

## 为什么使用 `TypedDict`

普通的 `dict[str, object]` 只说明键是字符串、值未知，无法告诉 mypy 某个固定字段的类型。`TypedDict` 可以描述固定键：

```python
summary: ResearchSummaryCore
question = summary["research_question"]
```

mypy 能推断 `question` 是 `str`。但 `TypedDict` 只参与静态类型检查，不会在运行时自动验证 `json.load()` 的结果，因此仍然需要 `validate_summary_core()`。

## 实现提示

- 不要急着使用 `cast()`；类型断言不能代替运行时校验。
- 校验外部字典后，显式取出三个字段并构造一个新字典，通常更容易让 mypy 理解。
- 错误信息至少应包含出错字段名，例如 `sample_size`。
- 这一小步暂不处理多余字段；返回的新字典只保留契约定义的三个字段。

## 测试要求

在 `week02/lesson02_validation/test_research_schema.py` 中至少编写以下测试：

1. 正整数样本量通过，返回值只包含三个契约字段。
2. `sample_size=None` 通过。
3. 顶层为列表时抛出 `TypeError`。
4. 使用参数化测试覆盖三个必需字段分别缺失。
5. 两个字符串字段分别为空字符串或只有空白时失败。
6. `sample_size` 为字符串时失败。
7. `sample_size` 为 `0` 或负数时失败。
8. `sample_size=True` 时失败。

重点区分 `TypeError` 与 `ValueError`，并检查错误消息包含相关字段名。不要只写 `pytest.raises(Exception)`。

## 验收标准

- 返回类型为 `ResearchSummaryCore`，不是宽泛的 `dict[str, object]` 或 `Any`。
- 未使用 `cast()`、`# type: ignore` 或静默类型转换绕过校验。
- 所有失败路径使用准确的异常类型，并提供可定位字段的错误信息。
- 测试不访问网络、不写仓库固定路径。
- Ruff、mypy strict 和 pytest 全部通过。

## 运行命令

```powershell
.\.venv\Scripts\ruff.exe check week02\lesson02_validation
.\.venv\Scripts\ruff.exe format --check week02\lesson02_validation
.\.venv\Scripts\mypy.exe --strict week02\lesson02_validation\research_schema.py week02\lesson02_validation\test_research_schema.py
.\.venv\Scripts\python.exe -m pytest week02\lesson02_validation\test_research_schema.py -q
```

## 完成后回复

```text
W2-02A 完成
用时：
测试数：
Ruff：
mypy：
pytest：
为什么 bool 需要单独拒绝：
TypedDict 与运行时校验的区别：
```
