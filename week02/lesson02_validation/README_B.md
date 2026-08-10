# W2-02B：完整研究摘要契约与列表字段校验

预计用时：45–75 分钟。本任务继续使用本地 Python 对象，不读取文件、不访问网络。

## 目标

在已经验收的 `ResearchSummaryCore` 基础上增加三个字段：

```python
class ResearchSummary(ResearchSummaryCore):
    statistical_methods: list[str]
    key_findings: list[str]
    limitations: list[str]
```

并实现：

```python
def validate_research_summary(data: object) -> ResearchSummary: ...
```

本次重点不只是检查“字段值是列表”，还要检查列表中的每个元素。

## 完整数据契约

| 字段 | 类型和值规则 |
|---|---|
| `research_question` | 非空字符串 |
| `data_source` | 非空字符串 |
| `sample_size` | 正整数或 `None`，拒绝 `bool` |
| `statistical_methods` | `list[str]`，允许空列表，每个字符串必须非空 |
| `key_findings` | `list[str]`，允许空列表，每个字符串必须非空 |
| `limitations` | `list[str]`，允许空列表，每个字符串必须非空 |

空列表表示摘要没有提供对应信息。字段本身仍是必需的，因此“缺少字段”和“字段为空列表”是两种不同情况。

## 实现要求

继续修改你自己的 `research_schema.py` 和 `test_research_schema.py`，不要修改参考文件。

1. 保留 `ResearchSummaryCore` 和 `validate_summary_core()` 的现有行为与测试。
2. 使用 `TypedDict` 继承定义 `ResearchSummary`。
3. 新增一个职责单一的私有辅助函数：

   ```python
   def _validate_string_list(value: object, field: str) -> list[str]: ...
   ```

4. 字段值不是 `list` 时抛出 `TypeError`，消息包含字段名。
5. 列表元素不是字符串时抛出 `TypeError`，消息同时包含字段名和元素索引。
6. 列表元素是空字符串或纯空白时抛出 `ValueError`，消息同时包含字段名和元素索引。
7. 允许空列表。
8. 返回结果只包含六个契约字段。
9. 返回新的列表，不能让校验结果与原始外部列表共享同一个可变对象。

可以复用 `validate_summary_core()`，但不要为了复用而修改它已经验收的接口。

## 为什么要复制列表

如果直接把外部列表放入结果中：

```text
外部代码修改原始列表
       ↓
已经“校验通过”的业务数据也被悄悄修改
```

构造新列表可以切断这层共享。这里先处理一层字符串列表；深层嵌套复制留到以后学习。

## 测试要求

在原有测试保持通过的基础上，至少覆盖：

1. 完整的六字段数据通过，并精确断言返回结果。
2. 三个列表字段均允许空列表。
3. 参数化覆盖三个列表字段分别缺失，消息包含字段名。
4. 参数化覆盖字段值为字符串、元组或 `None`，抛出 `TypeError`。
5. 参数化覆盖列表中包含整数，消息包含字段名和索引。
6. 参数化覆盖列表中包含空字符串或纯空白字符串，消息包含字段名和索引。
7. 输入包含额外字段时，返回结果不包含该字段。
8. 校验后修改原始列表，返回结果保持不变。

请测试行为，不要依赖辅助函数的内部实现细节。

## 验收标准

- 原有 W2-02A 的 14 条测试继续通过。
- 新增测试真正覆盖容器类型、元素类型、索引定位和列表复制。
- 没有使用 `Any`、`cast()`、`# type: ignore` 或第三方校验框架。
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
W2-02B 完成
用时：
新增测试数：
总测试数：
Ruff：
mypy：
pytest：
为什么需要验证列表元素：
为什么返回新列表：
```
